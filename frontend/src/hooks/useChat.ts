import { useCallback, useEffect, useRef, useState } from 'react';

interface Message {
  type: 'message' | 'handover' | 'ping';
  session_id: string;
  content: string;
  timestamp: string;
  metadata?: {
    level?: 1 | 2 | 3;
    source?: 'ai' | 'volunteer' | 'system';
  };
}

interface UseChatOptions {
  wsUrl: string;
  sessionId: string;
  onMessage?: (message: Message) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export function useChat({
  wsUrl,
  sessionId,
  onMessage,
  onError,
  onConnect,
  onDisconnect,
}: UseChatOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  // Conecta ao WebSocket
  useEffect(() => {
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      onConnect?.();
      console.log('WebSocket conectado');
    };

    ws.onmessage = (event) => {
      try {
        const message: Message = JSON.parse(event.data);
        setMessages((prev) => [...prev, message]);
        onMessage?.(message);
      } catch (error) {
        console.error('Erro ao parsear mensagem:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('Erro no WebSocket:', error);
      onError?.(error);
    };

    ws.onclose = () => {
      setIsConnected(false);
      onDisconnect?.();
      console.log('WebSocket desconectado');
    };

    return () => {
      ws.close();
    };
  }, [wsUrl, onMessage, onError, onConnect, onDisconnect]);

  // Envia mensagem
  const sendMessage = useCallback(
    (content: string, type: 'message' | 'handover' = 'message') => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error('WebSocket não está conectado');
        return;
      }

      const message: Message = {
        type,
        session_id: sessionId,
        content,
        timestamp: new Date().toISOString(),
        metadata: {
          level: 1,
        },
      };

      wsRef.current.send(JSON.stringify(message));
    },
    [sessionId]
  );

  // Solicita handover (troca para humano)
  const requestHandover = useCallback(() => {
    sendMessage('Gostaria de falar com um humano', 'handover');
  }, [sendMessage]);

  return {
    isConnected,
    messages,
    sendMessage,
    requestHandover,
  };
}
