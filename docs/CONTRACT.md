# Contrato de Interface - Comunicação entre Serviços

## Formato de Mensagens (JSON)

### 1. Mensagem do Cliente para Backend

```json
{
  "type": "message" | "handover" | "ping",
  "session_id": "uuid-v4",
  "content": "string",
  "timestamp": "ISO8601",
  "metadata": {
    "level": 1 | 2 | 3
  }
}
```

### 2. Mensagem Backend -> Agent (Python)

```json
{
  "session_id": "uuid-v4",
  "message": "string",
  "history": [
    {
      "role": "user" | "assistant",
      "content": "string",
      "timestamp": "ISO8601"
    }
  ],
  "context": {
    "level": 1,
    "language": "pt-BR"
  }
}
```

### 3. Resposta Agent -> Backend

```json
{
  "session_id": "uuid-v4",
  "response": "string",
  "metadata": {
    "model": "string",
    "tokens": 0,
    "should_handover": false,
    "handover_reason": "optional string"
  },
  "timestamp": "ISO8601"
}
```

### 4. Mensagem Backend -> Cliente

```json
{
  "type": "response" | "handover_notification" | "error",
  "content": "string",
  "timestamp": "ISO8601",
  "metadata": {
    "source": "ai" | "volunteer" | "system"
  }
}
```

## Fluxos de Comunicação

### Fluxo Normal (Nível 1 - IA)
```
Cliente --WS--> Backend --HTTP--> Agent --HTTP--> Backend --WS--> Cliente
```

### Fluxo Handover (Nível 1 -> 2)
```
Cliente --WS--> Backend (detecta handover) --> Redis Pub/Sub --> Volunteer Pool
```

## Regras de Segurança

- **Session ID**: UUID v4 gerado no cliente, volátil
- **Logs**: Apenas session_id e metadata, NUNCA o conteúdo
- **TTL**: Sessões expiram após 1h de inatividade
- **Rate Limiting**: 10 mensagens/minuto por sessão
