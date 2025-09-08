import { useRef, useCallback, useEffect } from 'react';
import { createChatWebSocket, closeWebSocket, ChatCompletionRequest } from '@/utils/websocketClient';

interface UseChatWebSocketOptions {
  onMessage: (message: string) => void;
  onError: (error: Event) => void;
  onClose: () => void;
}

export const useChatWebSocket = () => {
  const webSocketRef = useRef<WebSocket | null>(null);

  const connect = useCallback((
    requestBody: ChatCompletionRequest,
    options: UseChatWebSocketOptions
  ) => {
    // Close any existing connection
    closeWebSocket(webSocketRef.current);

    // Create new connection
    webSocketRef.current = createChatWebSocket(
      requestBody,
      options.onMessage,
      options.onError,
      options.onClose
    );

    return webSocketRef.current;
  }, []);

  const disconnect = useCallback(() => {
    closeWebSocket(webSocketRef.current);
    webSocketRef.current = null;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    isConnected: webSocketRef.current?.readyState === WebSocket.OPEN
  };
};
