# Guia de Desenvolvimento

## Pré-requisitos

- Docker & Docker Compose
- Go 1.21+
- Python 3.11+
- Node.js 20+
- Poetry (Python)

## Setup Local

### 1. Clonar e Configurar

```bash
git clone <repo>
cd amigo-imaginario
cp .env.example .env
# Adicionar OPENAI_API_KEY no .env
```

### 2. Instalar Dependências

```bash
# Agent (Python)
cd agent
poetry install
poetry run pre-commit install

# Backend (Go)
cd ../backend
go mod download

# Frontend (Next.js)
cd ../frontend
npm install
```

### 3. Rodar com Docker Compose

```bash
cd infra
docker-compose up --build
```

Serviços disponíveis:
- Frontend: http://localhost:3000
- Backend WS: ws://localhost:8080/ws
- Agent API: http://localhost:8000
- Redis: localhost:6379

## Desenvolvimento Individual

### Agent (Python)

```bash
cd agent
poetry run uvicorn src.main:app --reload
```

### Backend (Go)

```bash
cd backend
go run cmd/api/main.go
```

### Frontend (Next.js)

```bash
cd frontend
npm run dev
```

## Testes

### Python

```bash
cd agent
poetry run pytest
poetry run ruff check .
poetry run pyright
```

### Go

```bash
cd backend
go test ./...
golangci-lint run
```

### TypeScript

```bash
cd frontend
npm run lint
npm run type-check
```

## Estrutura de Commits

Seguir Conventional Commits:

```
feat(agent): adiciona detecção de crise
fix(backend): corrige leak de memória no Hub
docs: atualiza guia de arquitetura
```

## Debugging

### Logs

- Agent: `docker logs -f amigo-agent`
- Backend: `docker logs -f amigo-backend`
- Frontend: `docker logs -f amigo-frontend`

### Redis CLI

```bash
docker exec -it amigo-redis redis-cli
> MONITOR  # Ver comandos em tempo real
```

## Boas Práticas

1. **Nunca logar conteúdo de mensagens**
2. **Sempre validar Session ID**
3. **Usar tipos estritos (Pydantic, TypeScript)**
4. **Testar fluxos de handover**
5. **Documentar mudanças no CONTRACT.md**
