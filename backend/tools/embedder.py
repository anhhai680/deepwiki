import adalflow as adal

from backend.core.config import get_config_manager


def get_embedder() -> adal.Embedder:
    manager = get_config_manager()
    embedder_config = manager.get_embedder_config() or {}

    # --- Initialize Embedder ---
    # Get the embedder section configuration
    embedder_section = embedder_config.get("embedder", {})
    if not embedder_section:
        raise KeyError("embedder section not found in configuration")
    
    model_client_class = embedder_section.get("model_client")
    if model_client_class is None:
        raise KeyError("model_client not found in embedder configuration")

    # Initialize the model client
    if "initialize_kwargs" in embedder_section:
        model_client = model_client_class(**embedder_section["initialize_kwargs"])
    else:
        model_client = model_client_class()
    
    # Create the embedder
    embedder = adal.Embedder(
        model_client=model_client,
        model_kwargs=embedder_section.get("model_kwargs", {}),
    )
    return embedder
