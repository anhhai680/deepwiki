import { NextRequest, NextResponse } from 'next/server';

// The target backend server base URL, derived from environment variable or defaulted.
// This should match the logic in your frontend's page.tsx for consistency.
const TARGET_SERVER_BASE_URL = process.env.SERVER_BASE_URL || 'http://localhost:8001';

// This is a fallback HTTP implementation that will be used if WebSockets are not available
// or if there's an error with the WebSocket connection
export async function POST(req: NextRequest) {
  try {
    const requestBody = await req.json(); // Assuming the frontend sends JSON

    // Note: This endpoint now uses the HTTP fallback instead of WebSockets
    // The WebSocket implementation is in src/utils/websocketClient.ts
    // This HTTP endpoint is kept for backward compatibility
    console.log('Using HTTP fallback for chat completion instead of WebSockets');

    const targetUrl = `${TARGET_SERVER_BASE_URL}/api/chat/completions/stream`;
    console.log(`Proxying request to: ${targetUrl}`);

    // Create an AbortController with timeout for better error handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.log('Request timeout after 5 minutes, aborting...');
      controller.abort();
    }, 300000); // 5 minutes

    // Add a small delay to ensure backend is ready if running in Docker
    if (process.env.NODE_ENV === 'production') {
      console.log('Production mode - adding startup delay');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Make the actual request to the backend service with retry logic
    let backendResponse;
    let lastError;
    const maxRetries = 3;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`Attempt ${attempt}/${maxRetries} to reach backend`);
        
        backendResponse = await fetch(targetUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream', // Indicate that we expect a stream
          },
          body: JSON.stringify(requestBody),
          signal: controller.signal,
        });
        
        console.log(`Backend responded with status: ${backendResponse.status}`);
        break; // Success, exit retry loop
        
      } catch (error) {
        lastError = error;
        console.error(`Attempt ${attempt} failed:`, error);
        
        if (attempt < maxRetries) {
          const delay = Math.min(1000 * Math.pow(2, attempt), 5000); // Exponential backoff, max 5s
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    // Clear the timeout since we got a response or exhausted retries
    clearTimeout(timeoutId);
    
    if (!backendResponse) {
      throw lastError || new Error('Failed to connect to backend after retries');
    }

    // If the backend service returned an error, forward that error to the client
    if (!backendResponse.ok) {
      const errorBody = await backendResponse.text();
      const errorHeaders = new Headers();
      backendResponse.headers.forEach((value, key) => {
        errorHeaders.set(key, value);
      });
      return new NextResponse(errorBody, {
        status: backendResponse.status,
        statusText: backendResponse.statusText,
        headers: errorHeaders,
      });
    }

    // Ensure the backend response has a body to stream
    if (!backendResponse.body) {
      return new NextResponse('Stream body from backend is null', { status: 500 });
    }

    // Create a new ReadableStream to pipe the data from the backend to the client
    const stream = new ReadableStream({
      async start(controller) {
        const reader = backendResponse.body!.getReader();
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              break;
            }
            controller.enqueue(value);
          }
        } catch (error) {
          console.error('Error reading from backend stream in proxy:', error);
          controller.error(error);
        } finally {
          controller.close();
          reader.releaseLock(); // Important to release the lock on the reader
        }
      },
      cancel(reason) {
        console.log('Client cancelled stream request:', reason);
      }
    });

    // Set up headers for the response to the client
    const responseHeaders = new Headers();
    // Copy the Content-Type from the backend response (e.g., 'text/event-stream')
    const contentType = backendResponse.headers.get('Content-Type');
    if (contentType) {
      responseHeaders.set('Content-Type', contentType);
    }
    // It's good practice for streams not to be cached or transformed by intermediaries.
    responseHeaders.set('Cache-Control', 'no-cache, no-transform');

    return new NextResponse(stream, {
      status: backendResponse.status, // Should be 200 for a successful stream start
      headers: responseHeaders,
    });

  } catch (error) {
    console.error('Error in API proxy route (/api/chat/stream):', error);
    let errorMessage = 'Internal Server Error in proxy';
    let statusCode = 500;
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = 'Request timeout - the backend took too long to respond';
        statusCode = 504; // Gateway Timeout
      } else {
        errorMessage = error.message;
      }
    }
    
    return new NextResponse(JSON.stringify({ error: errorMessage }), {
      status: statusCode,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

// Optional: Handle OPTIONS requests for CORS if you ever call this from a different origin
// or use custom headers that trigger preflight requests. For same-origin, it's less critical.
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204, // No Content
    headers: {
      'Access-Control-Allow-Origin': '*', // Be more specific in production if needed
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization', // Adjust as per client's request headers
    },
  });
}