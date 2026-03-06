# Arquitetura do AMIGO

## Visão Geral

Sistema distribuído com 3 serviços principais orquestrados via Docker Compose.

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │ ◄─WS──► │   Backend   │ ◄─HTTP─►│    Agent    │
│  (Next.js)  │         │     (Go)    │         │  (Python)   │
└─────────────┘         └──────┬──────┘         └─────────────┘
                               │
                               │ Pub/Sub
                               ▼
                        ┌─────────────┐
                        │    Redis    │
                        └─────────────┘
```

## Componentes

### 1. Frontend (Next.js + TypeScript)

- Interface do usuário
- Comunicação via WebSocket
- Hook customizado `useChat` para gerenciar conexão
- Geração de Session ID (UUID v4) no cliente

### 2. Backend (Go)

- Gateway WebSocket (Hub pattern)
- Orquestrador de mensagens
- Roteamento entre níveis (IA/Humano/Catálogo)
- Integração com Redis para Pub/Sub
- Clean Architecture

### 3. Agent (Python)

- Motor de IA usando LangGraph
- StateGraph com checkpoint em memória (MemorySaver)
- Wrapper para LLM (OpenAI GPT-4)
- Detecção de necessidade de handover
- FastAPI para servir endpoints

### 4. Redis

- Pub/Sub para mensagens em tempo real
- Cache de sessões voláteis (TTL 1h)
- Fila de mensagens entre serviços

## Fluxos de Dados

### Fluxo Normal (Nível 1 - IA)

1. Usuário envia mensagem via WebSocket
2. Backend recebe e valida
3. Backend envia para Agent via HTTP POST
4. Agent processa com LangGraph + LLM
5. Agent retorna resposta
6. Backend envia resposta ao usuário via WebSocket

### Fluxo Handover (Nível 1 → 2)

1. Agent detecta necessidade de handover
2. Backend recebe flag `should_handover: true`
3. Backend publica mensagem no Redis (canal de voluntários)
4. Voluntário disponível aceita
5. Backend redireciona mensagens para voluntário

## Segurança

- **Anonimato**: Session ID volátil, sem persistência de identidade
- **Logs Seguros**: Apenas metadata, nunca conteúdo de mensagens
- **Rate Limiting**: 10 mensagens/minuto por sessão
- **TTL**: Sessões expiram após 1h de inatividade
- **CORS**: Configurado para domínios específicos em produção

## Escalabilidade

- Backend: Stateless, pode escalar horizontalmente
- Agent: Pool de workers via Gunicorn/Uvicorn
- Redis: Cluster para alta disponibilidade
- Frontend: CDN + Edge caching
