"""
WebSocket handler for wiki chat functionality.

This module handles WebSocket connections for real-time chat completions
with AI models, including RAG-powered responses and multi-provider support.
"""

import logging
import os
from typing import List, Optional, Dict, Any, Union
from urllib.parse import unquote

import google.generativeai as genai
from adalflow.components.model_client.ollama_client import OllamaClient
from backend.components.generator.base import ModelType
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field

from backend.core.config.settings import get_model_config, configs, OPENROUTER_API_KEY, OPENAI_API_KEY
from backend.utils.token_utils import count_tokens
from backend.utils.file_utils import get_file_content
from backend.utils.response_utils import merge_repository_results
from backend.components.generator.providers.openai_generator import OpenAIGenerator
from backend.components.generator.providers.openrouter_generator import OpenRouterGenerator
from backend.components.generator.providers.azure_generator import AzureAIGenerator
from backend.components.generator.providers.dashscope_generator import DashScopeGenerator
from backend.pipelines.rag import create_rag
from backend.models.chat import ChatCompletionRequest, ChatMessage

# Configure logging
from backend.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def handle_multiple_repositories(websocket: WebSocket, request: ChatCompletionRequest, input_too_large: bool):
    """Handle requests with multiple repositories"""
    try:
        all_results = []
        total_tokens = 0
        
        # Process each repository individually using existing RAG pipeline
        for i, repo_url in enumerate(request.repo_url):
            logger.info(f"Processing repository {i+1}/{len(request.repo_url)}: {repo_url}")
            
            # Create single repository request for each repo
            single_request = ChatCompletionRequest(
                repo_url=repo_url,
                messages=request.messages,
                filePath=request.filePath,
                token=request.token,
                type=request.type,
                provider=request.provider,
                model=request.model,
                language="en",
                excluded_dirs=request.excluded_dirs,
                excluded_files=request.excluded_files,
                included_dirs=request.included_dirs,
                included_files=request.included_files
            )
            
            # Process with existing single repository logic
            result = await process_single_repository_request(single_request, input_too_large)
            all_results.append({
                "repo_url": repo_url,
                "result": result,
                "index": i
            })
            
            # Progress updates are now logged only to avoid leaking JSON into client output
            logger.info(
                f"Progress: Processed repository {i+1}/{len(request.repo_url)}"
            )
        
        # Merge results from all repositories
        # The results already contain repo_url, just pass them directly
        logger.info(f"All results before merge: {[{k: v for k, v in item['result'].items() if k != 'content'} for item in all_results]}")
        actual_results = [item["result"] for item in all_results]
        merged_response = merge_repository_results(actual_results)
        logger.info(f"Merged response: {merged_response}")
        
        # Send final merged response as text (like single repository)
        # Extract the content from the merged response
        response_content = merged_response.get("content", "No content available")
        await websocket.send_text(response_content)
        await websocket.send_text("[DONE]")
        
    except Exception as e:
        logger.error(f"Error processing multiple repositories: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"Error processing multiple repositories: {str(e)}"}
        })


async def handle_single_repository(websocket: WebSocket, request: ChatCompletionRequest, input_too_large: bool):
    """Handle single repository request using existing logic"""
    # Create a new RAG instance for this request
    request_rag = create_rag(provider=request.provider, model=request.model)

    # Extract custom file filter parameters if provided
    excluded_dirs = None
    excluded_files = None
    included_dirs = None
    included_files = None

    if request.excluded_dirs:
        excluded_dirs = [unquote(dir_path) for dir_path in request.excluded_dirs.split('\n') if dir_path.strip()]
        logger.info(f"Using custom excluded directories: {excluded_dirs}")
    if request.excluded_files:
        excluded_files = [unquote(file_pattern) for file_pattern in request.excluded_files.split('\n') if file_pattern.strip()]
        logger.info(f"Using custom excluded files: {excluded_files}")
    if request.included_dirs:
        included_dirs = [unquote(dir_path) for dir_path in request.included_dirs.split('\n') if dir_path.strip()]
        logger.info(f"Using custom included directories: {included_dirs}")
    if request.included_files:
        included_files = [unquote(file_pattern) for file_pattern in request.included_files.split('\n') if file_pattern.strip()]
        logger.info(f"Using custom included files: {included_files}")

    request_rag.prepare_retriever(request.repo_url, request.type, request.token, excluded_dirs, excluded_files, included_dirs, included_files)
    logger.info(f"Retriever prepared for {request.repo_url}")

    # Validate request
    if not request.messages or len(request.messages) == 0:
        await websocket.send_text("Error: No messages provided")
        await websocket.close()
        return

    last_message = request.messages[-1]
    if last_message.role != "user":
        await websocket.send_text("Error: Last message must be from the user")
        await websocket.close()
        return

    # Process previous messages to build conversation history
    for i in range(0, len(request.messages) - 1, 2):
        if i + 1 < len(request.messages):
            user_msg = request.messages[i]
            assistant_msg = request.messages[i + 1]

            if user_msg.role == "user" and assistant_msg.role == "assistant":
                request_rag.memory.add_dialog_turn(
                    user_query=user_msg.content,
                    assistant_response=assistant_msg.content
                )

    # Check if this is a Deep Research request
    is_deep_research = False
    research_iteration = 1

    # Process messages to detect Deep Research requests
    for msg in request.messages:
        if hasattr(msg, 'content') and msg.content and "[DEEP RESEARCH]" in msg.content:
            is_deep_research = True
            # Only remove the tag from the last message
            if msg == request.messages[-1]:
                # Remove the Deep Research tag
                msg.content = msg.content.replace("[DEEP RESEARCH]", "").strip()

    # Count research iterations if this is a Deep Research request
    if is_deep_research:
        research_iteration = sum(1 for msg in request.messages if msg.role == 'assistant') + 1
        logger.info(f"Deep Research request detected - iteration {research_iteration}")

        # Check if this is a continuation request
        if "continue" in last_message.content.lower() and "research" in last_message.content.lower():
            # Find the original topic from the first user message
            original_topic = None
            for msg in request.messages:
                if msg.role == "user" and "continue" not in msg.content.lower():
                    original_topic = msg.content.replace("[DEEP RESEARCH]", "").strip()
                    logger.info(f"Found original research topic: {original_topic}")
                    break

            if original_topic:
                # Replace the continuation message with the original topic
                last_message.content = original_topic
                logger.info(f"Using original topic for research: {original_topic}")

    # Get the query from the last message
    query = last_message.content

    # Only retrieve documents if input is not too large
    context_text = ""
    retrieved_documents = None

    if not input_too_large:
        try:
            # If filePath exists, modify the query for RAG to focus on the file
            rag_query = query
            if request.filePath:
                # Use the file path to get relevant context about the file
                rag_query = f"Contexts related to {request.filePath}"
                logger.info(f"Modified RAG query to focus on file: {request.filePath}")

                            # Try to perform RAG retrieval
                try:
                    # This will use the actual RAG implementation
                    rag_answer, retrieved_documents = request_rag.call(rag_query, language=request.language or "en")
                    
                    # Debug: Log what the RAG pipeline returned
                    logger.info(f"RAG pipeline returned: rag_answer={rag_answer}, type={type(rag_answer)}")
                    if rag_answer:
                        logger.info(f"RAG answer content: {str(rag_answer)[:200]}...")
                    
                    # Use the RAG answer directly instead of building a new prompt
                    if rag_answer:
                        logger.info("RAG pipeline generated response, streaming directly")
                        # Stream the RAG answer directly to the WebSocket
                        await websocket.send_text(str(rag_answer))
                        await websocket.send_text("[DONE]")
                        return
                    else:
                        logger.warning("RAG pipeline returned empty response")

                    if retrieved_documents and retrieved_documents[0].documents:
                        # Format context for the prompt in a more structured way
                        documents = retrieved_documents[0].documents
                        logger.info(f"Retrieved {len(documents)} documents")

                        # Group documents by file path
                        docs_by_file = {}
                        for doc in documents:
                            file_path = doc.meta_data.get('file_path', 'unknown')
                            if file_path not in docs_by_file:
                                docs_by_file[file_path] = []
                            docs_by_file[file_path].append(doc)

                        # Format context text with file path grouping
                        context_parts = []
                        for file_path, docs in docs_by_file.items():
                            # Add file header with metadata
                            header = f"## File Path: {file_path}\n\n"
                            # Add document content
                            content = "\n\n".join([doc.text for doc in docs])

                            context_parts.append(f"{header}{content}")

                        # Join all parts with clear separation
                        context_text = "\n\n" + "-" * 10 + "\n\n".join(context_parts)
                    else:
                        logger.warning("No documents retrieved from RAG")
                except Exception as e:
                    logger.error(f"Error in RAG retrieval: {str(e)}")
                    # Continue without RAG if there's an error

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            context_text = ""

    # Get repository information
    repo_url = request.repo_url
    repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url

    # Determine repository type
    repo_type = request.type

    # Get language information
    # Force English for DeepWiki chat responses
    language_code = "en"
    supported_langs = configs["lang_config"]["supported_languages"]
    language_name = supported_langs.get(language_code, "English")

    # Create system prompt
    if is_deep_research:
        # Check if this is the first iteration
        is_first_iteration = research_iteration == 1

        # Check if this is the final iteration
        is_final_iteration = research_iteration >= 5

        if is_first_iteration:
            system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You are conducting a multi-turn Deep Research process to thoroughly investigate the specific topic in the user's query.
Your goal is to provide detailed, focused information EXCLUSIVELY about this topic.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- This is the first iteration of a multi-turn research process focused EXCLUSIVELY on the user's query
- Start your response with "## Research Plan"
- Outline your approach to investigating this specific topic
- If the topic is about a specific file or feature (like "Dockerfile"), focus ONLY on that file or feature
- Clearly state the specific topic you're researching to maintain focus throughout all iterations
- Identify the key aspects you'll need to research
- Provide initial findings based on the information available
- End with "## Next Steps" indicating what you'll investigate in the next iteration
- Do NOT provide a final conclusion yet - this is just the beginning of the research
- Do NOT include general repository information unless directly relevant to the query
- Focus EXCLUSIVELY on the specific topic being researched - do not drift to related topics
- Your research MUST directly address the original question
- NEVER respond with just "Continue the research" as an answer - always provide substantive research findings
- Remember that this topic will be maintained across all research iterations
</guidelines>

<style>
- Be concise but thorough
- Use markdown formatting to improve readability
- Cite specific files and code sections when relevant
</style>"""
        elif is_final_iteration:
            system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You are in the final iteration of a Deep Research process focused EXCLUSIVELY on the latest user query.
Your goal is to synthesize all previous findings and provide a comprehensive conclusion that directly addresses this specific topic and ONLY this topic.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- This is the final iteration of the research process
- CAREFULLY review the entire conversation history to understand all previous findings
- Synthesize ALL findings from previous iterations into a comprehensive conclusion
- Start with "## Final Conclusion"
- Your conclusion MUST directly address the original question
- Stay STRICTLY focused on the specific topic - do not drift to related topics
- Include specific code references and implementation details related to the topic
- Highlight the most important discoveries and insights about this specific functionality
- Provide a complete and definitive answer to the original question
- Do NOT include general repository information unless directly relevant to the query
- Focus exclusively on the specific topic being researched
- NEVER respond with "Continue the research" as an answer - always provide a complete conclusion
- If the topic is about a specific file or feature (like "Dockerfile"), focus ONLY on that file or feature
- Ensure your conclusion builds on and references key findings from previous iterations
</guidelines>

<style>
- Be concise but thorough
- Use markdown formatting to improve readability
- Cite specific files and code sections when relevant
- Structure your response with clear headings
- End with actionable insights or recommendations when appropriate
</style>"""
        else:
            system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You are currently in iteration {research_iteration} of a Deep Research process focused EXCLUSIVELY on the latest user query.
Your goal is to build upon previous research iterations and go deeper into this specific topic without deviating from it.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- CAREFULLY review the conversation history to understand what has been researched so far
- Your response MUST build on previous research iterations - do not repeat information already covered
- Identify gaps or areas that need further exploration related to this specific topic
- Focus on one specific aspect that needs deeper investigation in this iteration
- Start your response with "## Research Update {research_iteration}"
- Clearly explain what you're investigating in this iteration
- Provide new insights that weren't covered in previous iterations
- If this is iteration 3, prepare for a final conclusion in the next iteration
- Do NOT include general repository information unless directly relevant to the query
- Focus EXCLUSIVELY on the specific topic being researched - do not drift to related topics
- If the topic is about a specific file or feature (like "Dockerfile"), focus ONLY on that file or feature
- NEVER respond with just "Continue the research" as an answer - always provide substantive research findings
- Your research MUST directly address the original question
- Maintain continuity with previous research iterations - this is a continuous investigation
</guidelines>

<style>
- Be concise but thorough
- Focus on providing new information, not repeating what's already been covered
- Use markdown formatting to improve readability
- Cite specific files and code sections when relevant
</style>"""
    else:
        system_prompt = f"""<role>
You are an expert code analyst examining the {repo_type} repository: {repo_url} ({repo_name}).
You provide direct, concise, and accurate information about code repositories.
You NEVER start responses with markdown headers or code fences.
IMPORTANT:You MUST respond in {language_name} language.
</role>

<guidelines>
- Answer the user's question directly without ANY preamble or filler phrases
- DO NOT include any rationale, explanation, or extra comments.
- Strictly base answers ONLY on existing code or documents
- DO NOT speculate or invent citations.
- DO NOT start with preambles like "Okay, here's a breakdown" or "Here's an explanation"
- DO NOT start with markdown headers like "## Analysis of..." or any file path references
- DO NOT start with ```markdown code fences
- DO NOT end your response with ``` closing fences
- DO NOT start by repeating or acknowledging the question
- JUST START with the direct answer to the question

<example_of_what_not_to_do>
```markdown
## Analysis of `adalflow/adalflow/datasets/gsm8k.py`

This file contains...
```
</example_of_what_not_to_do>

- Format your response with proper markdown including headings, lists, and code blocks WITHIN your answer
- For code analysis, organize your response with clear sections
- Think step by step and structure your answer logically
- Start with the most relevant information that directly addresses the user's query
- Be precise and technical when discussing code
- Always respond strictly in the configured language (do not mirror the user's query language)
</guidelines>

<style>
- Use concise, direct language
- Prioritize accuracy over verbosity
- When showing code, include line numbers and file paths when relevant
- Use markdown formatting to improve readability
</style>"""

    # Fetch file content if provided
    file_content = ""
    if request.filePath:
        try:
            file_content = get_file_content(request.repo_url, request.filePath, request.type, request.token)
            logger.info(f"Successfully retrieved content for file: {request.filePath}")
        except Exception as e:
            logger.error(f"Error retrieving file content: {str(e)}")
            # Continue without file content if there's an error

    # Format conversation history
    conversation_history = ""
    for turn_id, turn in request_rag.memory.call().items():
        if not isinstance(turn_id, int) and hasattr(turn, 'user_query') and hasattr(turn, 'assistant_response'):
            conversation_history += f"<turn>\n<user>{turn.user_query.query_str}</user>\n<assistant>{turn.assistant_response.response_str}</assistant>\n</turn>\n"

    # Create the prompt with context
    prompt = f"/no_think {system_prompt}\n\n"

    if conversation_history:
        prompt += f"<conversation_history>\n{conversation_history}</conversation_history>\n\n"

    # Check if filePath is provided and fetch file content if it exists
    if file_content:
        # Add file content to the prompt after conversation history
        prompt += f"<currentFileContent path=\"{request.filePath}\">\n{file_content}\n</currentFileContent>\n\n"

    # Only include context if it's not empty
    CONTEXT_START = "<START_OF_CONTEXT>"
    CONTEXT_END = "<END_OF_CONTEXT>"
    if context_text.strip():
        prompt += f"{CONTEXT_START}\n{context_text}\n{CONTEXT_END}\n\n"
    else:
        # Add a note that we're skipping RAG due to size constraints or because it's the isolated API
        logger.info("No context available from RAG")
        prompt += "<note>Answering without retrieval augmentation.</note>\n\n"

    # Strong language enforcement: English only
    prompt += "<language_policy>All output MUST be in English only. Do not mirror user's language. If any non-English appears, rewrite it to English before sending.</language_policy>\n\n"
    prompt += f"<query>\n{query}\n</query>\n\nAssistant: "

    try:
        full_config = get_model_config(request.provider, request.model)
        model_config = full_config["model_kwargs"]
        logger.info(f"Model configuration loaded successfully for {request.provider}/{request.model}")
    except Exception as e_config:
        logger.error(f"Failed to load model configuration: {str(e_config)}")
        error_msg = f"\nError: Failed to load model configuration for {request.provider}/{request.model}.\n\nError details: {str(e_config)}"
        await websocket.send_text(error_msg)
        await websocket.close()
        return

    if request.provider == "ollama":
        prompt += " /no_think"

        model = OllamaClient()
        model_kwargs = {
            "model": full_config["model"],
            "stream": True,
            "options": {
                "temperature": model_config["temperature"],
                "top_p": model_config["top_p"],
                "num_ctx": model_config.get("num_ctx", 4096)
            }
        }

        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
    elif request.provider == "openrouter":
        logger.info(f"Using OpenRouter with model: {request.model}")

        # Check if OpenRouter API key is set
        if not OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not configured, but continuing with request")
            # We'll let the OpenRouterGenerator handle this and return a friendly error message

        model = OpenRouterGenerator()
        model_kwargs = {
            "model": request.model,
            "stream": True,
            "temperature": model_config["temperature"]
        }
        # Only add top_p if it exists in the model config
        if "top_p" in model_config:
            model_kwargs["top_p"] = model_config["top_p"]

        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
    elif request.provider == "openai":
        logger.info(f"Using Openai protocol with model: {request.model}")

        # Check if an API key is set for Openai
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not configured, but continuing with request")
            # We'll let the OpenAIGenerator handle this and return an error message

        # Initialize Openai client
        try:
            model = OpenAIGenerator()
        except Exception as e_init:
            logger.error(f"Failed to initialize OpenAIGenerator: {str(e_init)}")
            error_msg = f"\nError: Failed to initialize OpenAI client. Please check that you have set the OPENAI_API_KEY environment variable with a valid API key.\n\nError details: {str(e_init)}"
            await websocket.send_text(error_msg)
            await websocket.close()
            return
        model_kwargs = {
            "model": request.model,
            "stream": True,
            "temperature": model_config["temperature"]
        }
        # Only add top_p if it exists in the model config
        if "top_p" in model_config:
            model_kwargs["top_p"] = model_config["top_p"]

        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
    elif request.provider == "azure":
        logger.info(f"Using Azure AI with model: {request.model}")

        # Initialize Azure AI client
        try:
            model = AzureAIGenerator()
        except Exception as e_init:
            logger.error(f"Failed to initialize AzureAIGenerator: {str(e_init)}")
            error_msg = f"\nError: Failed to initialize Azure AI client. Please check that you have set the required Azure environment variables.\n\nError details: {str(e_init)}"
            await websocket.send_text(error_msg)
            await websocket.close()
            return
        model_kwargs = {
            "model": request.model,
            "stream": True,
            "temperature": model_config["temperature"],
            "top_p": model_config["top_p"]
        }

        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
    elif request.provider == "dashscope":
        logger.info(f"Using Dashscope with model: {request.model}")

        # Initialize Azure AI client
        model = DashScopeGenerator()
        model_kwargs = {
            "model": request.model,
            "stream": True,
            "temperature": model_config["temperature"],
            "top_p": model_config["top_p"]
        }

        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
    elif request.provider == "privatemodel":
        logger.info(f"Using PrivateModel with model: {request.model}")

        # Import and initialize PrivateModel client
        from backend.components.generator.providers.private_model_generator import PrivateModelGenerator
        
        try:
            model = PrivateModelGenerator()
        except Exception as e_init:
            logger.error(f"Failed to initialize PrivateModelGenerator: {str(e_init)}")
            error_msg = f"\nError: Failed to initialize Private Model client. Please check that you have set the PRIVATE_MODEL_API_KEY environment variable if required.\n\nError details: {str(e_init)}"
            await websocket.send_text(error_msg)
            await websocket.close()
            return
        
        model_kwargs = {
            "model": request.model,
            "stream": True,
            "temperature": model_config["temperature"]
        }
        
        # Only add top_p if it exists in the model config
        if "top_p" in model_config:
            model_kwargs["top_p"] = model_config["top_p"]

        api_kwargs = model.convert_inputs_to_api_kwargs(
            input=prompt,
            model_kwargs=model_kwargs,
            model_type=ModelType.LLM
        )
    else:
        # Initialize Google Generative AI model
        model = genai.GenerativeModel(
            model_name=model_config["model"],
            generation_config={
                "temperature": model_config["temperature"],
                "top_p": model_config["top_p"],
                "top_k": model_config["top_k"]
            }
        )

    # Process the response based on the provider
    try:
        if request.provider == "ollama":
            # Get the response and handle it properly using the previously created api_kwargs
            response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
            # Handle streaming response from Ollama
            async for chunk in response:
                text = getattr(chunk, 'response', None) or getattr(chunk, 'text', None) or str(chunk)
                if text and not text.startswith('model=') and not text.startswith('created_at='):
                    text = text.replace('<think>', '').replace('</think>', '')
                    await websocket.send_text(text)
            # Send completion signal instead of closing connection
            await websocket.send_text("[DONE]")
        elif request.provider == "openrouter":
            try:
                # Get the response and handle it properly using the previously created api_kwargs
                logger.info("Making OpenRouter API call")
                response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                # Handle streaming response from OpenRouter
                async for chunk in response:
                    await websocket.send_text(chunk)
                # Send completion signal instead of closing connection
                await websocket.send_text("[DONE]")
            except Exception as e_openrouter:
                logger.error(f"Error with OpenRouter API: {str(e_openrouter)}")
                error_msg = f"\nError with OpenRouter API: {str(e_openrouter)}\n\nPlease check that you have set the OPENROUTER_API_KEY environment variable with a valid API key."
                await websocket.send_text(error_msg)
                # Close the WebSocket connection after sending the error message
                await websocket.close()
        elif request.provider == "openai":
            try:
                # Get the response and handle it properly using the previously created api_kwargs
                logger.info("Making Openai API call")
                logger.info(f"API kwargs: {api_kwargs}")
                response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                logger.info("OpenAI API call completed, processing response...")
                
                chunk_count = 0
                # Handle streaming response from Openai
                async for chunk in response:
                    try:
                        chunk_count += 1
                        choices = getattr(chunk, "choices", [])
                        if len(choices) > 0:
                            choice = choices[0]
                            delta = getattr(choice, "delta", None)
                            if delta is not None:
                                text = getattr(delta, "content", None)
                                if text is not None:
                                    await websocket.send_text(text)
                    except Exception as e_chunk:
                        logger.error(f"Error processing chunk {chunk_count}: {str(e_chunk)}")
                        import traceback
                        logger.error(f"Chunk processing traceback: {traceback.format_exc()}")
                
                logger.info(f"Total chunks processed: {chunk_count}")
                # Send completion signal instead of closing connection
                await websocket.send_text("[DONE]")
            except Exception as e_openai:
                logger.error(f"Error with Openai API: {str(e_openai)}")
                error_msg = f"\nError with Openai API: {str(e_openai)}\n\nPlease check that you have set the OPENAI_API_KEY environment variable with a valid API key."
                await websocket.send_text(error_msg)
                # Close the WebSocket connection after sending the error message
                await websocket.close()
        elif request.provider == "azure":
            try:
                # Get the response and handle it properly using the previously created api_kwargs
                logger.info("Making Azure AI API call")
                response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                # Handle streaming response from Azure AI
                async for chunk in response:
                    choices = getattr(chunk, "choices", [])
                    if len(choices) > 0:
                        delta = getattr(chunk, "delta", None)
                        if delta is not None:
                            text = getattr(delta, "content", None)
                            if text is not None:
                                await websocket.send_text(text)
                # Send completion signal instead of closing connection
                await websocket.send_text("[DONE]")
            except Exception as e_azure:
                logger.error(f"Error with Azure AI API: {str(e_azure)}")
                error_msg = f"\nError with Azure AI API: {str(e_azure)}\n\nPlease check that you have set the AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_VERSION environment variables with valid values."
                await websocket.send_text(error_msg)
                # Close the WebSocket connection after sending the error message
                await websocket.close()
        elif request.provider == "privatemodel":
            try:
                # Get the response and handle it properly using the previously created api_kwargs
                logger.info("Making PrivateModel API call")
                response = await model.acall(api_kwargs=api_kwargs, model_type=ModelType.LLM)
                logger.info("PrivateModel API call completed, processing response...")
                
                chunk_count = 0
                # Handle streaming response from PrivateModel (OpenAI-compatible)
                async for chunk in response:
                    try:
                        chunk_count += 1
                        choices = getattr(chunk, "choices", [])
                        if len(choices) > 0:
                            choice = choices[0]
                            delta = getattr(choice, "delta", None)
                            if delta is not None:
                                text = getattr(delta, "content", None)
                                if text is not None:
                                    await websocket.send_text(text)
                    except Exception as e_chunk:
                        logger.error(f"Error processing PrivateModel chunk {chunk_count}: {str(e_chunk)}")
                        import traceback
                        logger.error(f"PrivateModel chunk processing traceback: {traceback.format_exc()}")
                
                logger.info(f"Total PrivateModel chunks processed: {chunk_count}")
                # Send completion signal instead of closing connection
                await websocket.send_text("[DONE]")
            except Exception as e_privatemodel:
                logger.error(f"Error with PrivateModel API: {str(e_privatemodel)}")
                error_msg = f"\nError with PrivateModel API: {str(e_privatemodel)}\n\nPlease check that your private model deployment is running and accessible, and that you have set the PRIVATE_MODEL_API_KEY environment variable if required."
                await websocket.send_text(error_msg)
                # Close the WebSocket connection after sending the error message
                await websocket.close()
        else:
            # Generate streaming response
            response = model.generate_content(prompt, stream=True)
            # Stream the response
            for chunk in response:
                if hasattr(chunk, 'text'):
                    await websocket.send_text(chunk.text)
            # Send completion signal instead of closing connection
            await websocket.send_text("[DONE]")

    except Exception as e_outer:
        logger.error(f"Error in streaming response: {str(e_outer)}")
        error_message = str(e_outer)

        # Check for token limit errors
        if "maximum context length" in error_message or "token limit" in error_message or "too many tokens" in error_message:
            # If we hit a token limit error, try again without context
            logger.warning("Token limit exceeded, retrying without context")
            try:
                # Create a simplified prompt without context
                simplified_prompt = f"/no_think {system_prompt}\n\n"
                if conversation_history:
                    simplified_prompt += f"<conversation_history>\n{conversation_history}</conversation_history>\n\n"

                # Include file content in the fallback prompt if it was retrieved
                if request.filePath and file_content:
                    simplified_prompt += f"<currentFileContent path=\"{request.filePath}\">\n{file_content}\n</currentFileContent>\n\n"

                simplified_prompt += "<note>Answering without retrieval augmentation due to input size constraints.</note>\n\n"
                simplified_prompt += f"<query>\n{query}\n</query>\n\nAssistant: "

                if request.provider == "ollama":
                    simplified_prompt += " /no_think"

                    # Create new api_kwargs with the simplified prompt
                    fallback_model_kwargs = {
                        "model": full_config["model"],
                        "stream": True,
                        "options": {
                            "temperature": model_config["temperature"],
                            "top_p": model_config["top_p"],
                            "num_ctx": model_config.get("num_ctx", 4096)
                        }
                    }
                    fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                        input=simplified_prompt,
                        model_kwargs=fallback_model_kwargs,
                        model_type=ModelType.LLM
                    )

                    # Get the response using the simplified prompt
                    fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                    # Handle streaming fallback_response from Ollama
                    async for chunk in fallback_response:
                        text = getattr(chunk, 'response', None) or getattr(chunk, 'text', None) or str(chunk)
                        if text and not text.startswith('model=') and not text.startswith('created_at='):
                            text = text.replace('<think>', '').replace('</think>', '')
                            await websocket.send_text(text)
                    # Send completion signal instead of closing connection
                    await websocket.send_text("[DONE]")
                elif request.provider == "openrouter":
                    try:
                        # Create new api_kwargs with the simplified prompt
                        fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                            input=simplified_prompt,
                            model_kwargs=model_kwargs,
                            model_type=ModelType.LLM
                        )

                        # Get the response using the simplified prompt
                        logger.info("Making fallback OpenRouter API call")
                        fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                        # Handle streaming fallback_response from OpenRouter
                        async for chunk in fallback_response:
                            await websocket.send_text(chunk)
                        # Send completion signal instead of closing connection
                        await websocket.send_text("[DONE]")
                    except Exception as e_fallback:
                        logger.error(f"Error with OpenRouter API fallback: {str(e_fallback)}")
                        error_msg = f"\nError with OpenRouter API fallback: {str(e_fallback)}\n\nPlease check that you have set the OPENROUTER_API_KEY environment variable with a valid API key."
                        await websocket.send_text(error_msg)
                elif request.provider == "openai":
                    try:
                        # Create new api_kwargs with the simplified prompt
                        fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                            input=simplified_prompt,
                            model_kwargs=model_kwargs,
                            model_type=ModelType.LLM
                        )

                        # Get the response using the simplified prompt
                        logger.info("Making fallback Openai API call")
                        fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                        # Handle streaming fallback_response from Openai
                        async for chunk in fallback_response:
                            text = chunk if isinstance(chunk, str) else getattr(chunk, 'text', str(chunk))
                            await websocket.send_text(text)
                        # Send completion signal instead of closing connection
                        await websocket.send_text("[DONE]")
                    except Exception as e_fallback:
                        logger.error(f"Error with Openai API fallback: {str(e_fallback)}")
                        error_msg = f"\nError with Openai API fallback: {str(e_fallback)}\n\nPlease check that you have set the OPENAI_API_KEY environment variable with a valid API key."
                        await websocket.send_text(error_msg)
                elif request.provider == "azure":
                    try:
                        # Create new api_kwargs with the simplified prompt
                        fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                            input=simplified_prompt,
                            model_kwargs=model_kwargs,
                            model_type=ModelType.LLM
                        )

                        # Get the response using the simplified prompt
                        logger.info("Making fallback Azure AI API call")
                        fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                        # Handle streaming fallback response from Azure AI
                        async for chunk in fallback_response:
                            choices = getattr(chunk, "choices", [])
                            if len(choices) > 0:
                                delta = getattr(chunk, "delta", None)
                                if delta is not None:
                                    text = getattr(delta, "content", None)
                                    if text is not None:
                                        await websocket.send_text(text)
                        # Send completion signal instead of closing connection
                        await websocket.send_text("[DONE]")
                    except Exception as e_fallback:
                        logger.error(f"Error with Azure AI API fallback: {str(e_fallback)}")
                        error_msg = f"\nError with Azure AI API fallback: {str(e_fallback)}\n\nPlease check that you have set the AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_VERSION environment variables with valid values."
                        await websocket.send_text(error_msg)
                elif request.provider == "privatemodel":
                    try:
                        # Create new api_kwargs with the simplified prompt
                        fallback_api_kwargs = model.convert_inputs_to_api_kwargs(
                            input=simplified_prompt,
                            model_kwargs=model_kwargs,
                            model_type=ModelType.LLM
                        )

                        # Get the response using the simplified prompt
                        logger.info("Making fallback PrivateModel API call")
                        fallback_response = await model.acall(api_kwargs=fallback_api_kwargs, model_type=ModelType.LLM)

                        # Handle streaming fallback response from PrivateModel (OpenAI-compatible)
                        async for chunk in fallback_response:
                            choices = getattr(chunk, "choices", [])
                            if len(choices) > 0:
                                choice = choices[0]
                                delta = getattr(choice, "delta", None)
                                if delta is not None:
                                    text = getattr(delta, "content", None)
                                    if text is not None:
                                        await websocket.send_text(text)
                        # Send completion signal instead of closing connection
                        await websocket.send_text("[DONE]")
                    except Exception as e_fallback:
                        logger.error(f"Error with PrivateModel API fallback: {str(e_fallback)}")
                        error_msg = f"\nError with PrivateModel API fallback: {str(e_fallback)}\n\nPlease check that your private model deployment is running and accessible."
                        await websocket.send_text(error_msg)
                else:
                    # Initialize Google Generative AI model
                    model_config = get_model_config(request.provider, request.model)
                    fallback_model = genai.GenerativeModel(
                        model_name=model_config["model"],
                        generation_config={
                            "temperature": model_config["model_kwargs"].get("temperature", 0.7),
                            "top_p": model_config["model_kwargs"].get("top_p", 0.8),
                            "top_k": model_config["model_kwargs"].get("top_k", 40)
                        }
                    )

                    # Get streaming response using simplified prompt
                    fallback_response = fallback_model.generate_content(simplified_prompt, stream=True)
                    # Stream the fallback response
                    for chunk in fallback_response:
                        if hasattr(chunk, 'text'):
                            await websocket.send_text(chunk.text)
                    # Send completion signal instead of closing connection
                    await websocket.send_text("[DONE]")
            except Exception as e2:
                logger.error(f"Error in fallback streaming response: {str(e2)}")
                await websocket.send_text(f"\nI apologize, but your request is too large for me to process. Please try a shorter query or break it into smaller parts.")
                # Close the WebSocket connection after sending the error message
                await websocket.close()
        else:
            # For other errors, return the error message
            await websocket.send_text(f"\nError: {error_message}")
            # Close the WebSocket connection after sending the error message
            await websocket.close()

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {str(e)}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
            await websocket.close()
        except:
            pass


async def process_single_repository_request(request: ChatCompletionRequest, input_too_large: bool):
    """Process a single repository request using existing RAG pipeline"""
    try:
        # Create a new RAG instance for this request
        request_rag = create_rag(provider=request.provider, model=request.model)
        
        # Prepare retriever (existing logic)
        request_rag.prepare_retriever(
            request.repo_url, 
            request.type, 
            request.token, 
            request.excluded_dirs, 
            request.excluded_files, 
            request.included_dirs, 
            request.included_files
        )
        
        # Get the query from the last message
        query = request.messages[-1].content
        
        # If filePath exists, modify the query for RAG to focus on the file
        rag_query = query
        if request.filePath:
            rag_query = f"Contexts related to {request.filePath}"
            logger.info(f"Modified RAG query to focus on file: {request.filePath}")
        
        # Perform RAG retrieval (existing logic)
        rag_answer, retrieved_documents = request_rag.call(rag_query, language="en")
        
        # Debug: Log the RAG answer details
        logger.info(f"RAG answer type: {type(rag_answer)}")
        logger.info(f"RAG answer attributes: {dir(rag_answer) if rag_answer else 'None'}")
        if rag_answer:
            if hasattr(rag_answer, 'answer'):
                logger.info(f"RAG answer.answer: {rag_answer.answer[:200]}...")
            else:
                logger.info(f"RAG answer content: {str(rag_answer)[:200]}...")
        
        # Generate response (existing logic)
        if rag_answer:
            response = rag_answer.answer if hasattr(rag_answer, 'answer') else str(rag_answer)
        else:
            response = "I couldn't find relevant information in the repository to answer your question."
        
        return {
            "content": response,
            "repo_url": request.repo_url,
            "tokens_used": len(response.split()) if response else 0,
            "documents_retrieved": len(retrieved_documents[0].documents) if retrieved_documents and len(retrieved_documents) > 0 and hasattr(retrieved_documents[0], 'documents') else 0
        }
        
    except Exception as e:
        logger.error(f"Error processing repository {request.repo_url}: {e}")
        return {
            "content": f"Error processing repository: {str(e)}",
            "repo_url": request.repo_url,
            "error": str(e),
            "tokens_used": 0,
            "documents_retrieved": 0
        }


# Models are now imported from backend.models.chat

async def handle_websocket_chat(websocket: WebSocket):
    """
    Handle WebSocket connection for chat completions.
    This replaces the HTTP streaming endpoint with a WebSocket connection.
    """
    await websocket.accept()

    try:
        logger.info("WebSocket connection accepted")

        # Receive and parse the request data
        request_data = await websocket.receive_json()
        request = ChatCompletionRequest(**request_data)

        # Check if request contains very large input
        input_too_large = False
        if request.messages and len(request.messages) > 0:
            last_message = request.messages[-1]
            if hasattr(last_message, 'content') and last_message.content:
                tokens = count_tokens(last_message.content, request.provider == "ollama")
                logger.info(f"Request size: {tokens} tokens")
                if tokens > 8000:
                    logger.warning(f"Request exceeds recommended token limit ({tokens} > 7500)")
                    input_too_large = True

        # NEW: Check if multiple repositories are requested
        if isinstance(request.repo_url, list):
            # Multiple repositories - process each one individually
            await handle_multiple_repositories(websocket, request, input_too_large)
        else:
            # Single repository - use existing logic unchanged
            await handle_single_repository(websocket, request, input_too_large)

    except WebSocketDisconnect as e:
        logger.error(f"WebSocket disconnected: {str(e)}")
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {str(e)}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
            await websocket.close()
        except:
            pass
