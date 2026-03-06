# AMIGO Agent - Motor de IA

Motor de inferência multi-nível com LangGraph para assistência em saúde mental.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    GRAFO PRINCIPAL                          │
│                                                             │
│  Security → Risk Analysis → RAG → Generator → Judge         │
│                    ↓                              ↓         │
│              [Handover Decision]            [Handover]      │
└─────────────────────────────────────────────────────────────┘
```

## Nós do Grafo

1. **Security**: Sanitização e detecção de injeção de prompt
2. **Risk Analysis**: Score de risco (0-1) e detecção de crise
3. **RAG**: Recuperação de contexto de guias de psicologia
4. **Generator**: Persona "Amigo Imaginário" com LLM
5. **Judge**: Validação ética e compliance
6. **Handover**: Decisão de transição para humano

## Subgrafos

- **RAG Engine**: Busca semântica em vector store (FAISS)
- **Handover**: Lógica de transição e emissão de sinal

## Configuração

Variáveis de ambiente (`.env`):

```bash
# API Keys
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Modelos
DEFAULT_MODEL=gpt-4
FALLBACK_MODEL=gpt-3.5-turbo

# Thresholds
RISK_THRESHOLD_MEDIUM=0.4
RISK_THRESHOLD_HIGH=0.7
RISK_THRESHOLD_CRITICAL=0.9

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Instalação

```bash
poetry install
poetry run pre-commit install
```

## Desenvolvimento

```bash
# Rodar servidor
poetry run python -m src.main

# Testes
poetry run pytest

# Linting
poetry run ruff check .
poetry run pyright

# Rebuild vector store
poetry run python -c "from src.tools.vector_store import vector_store; vector_store.rebuild()"
```

## Adicionando Guias de Psicologia

1. Adicione arquivos `.md` em `data/psychology_guides/`
2. Rebuild o vector store
3. Reinicie o agent

Exemplo de guia:

```markdown
# Técnicas de Escuta Ativa

## Validação Emocional
- Reconheça os sentimentos sem julgamento
- Use frases como "Entendo que você está se sentindo..."
- Evite minimizar: "Não é tão grave assim"

## Perguntas Abertas
- "Como você está se sentindo em relação a isso?"
- "O que você acha que poderia ajudar?"
```

## Segurança

- Logs NUNCA registram conteúdo de mensagens
- Apenas session_id e metadata são logados
- Sanitização automática de inputs
- Validação ética em todas as respostas
