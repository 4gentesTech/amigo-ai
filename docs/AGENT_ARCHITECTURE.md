# Arquitetura Detalhada do Agent

## Visão Geral

O Agent é um sistema multi-camadas baseado em LangGraph que processa conversas de saúde mental com foco em segurança, ética e detecção de crises.

## Fluxo de Processamento

```
┌──────────────┐
│   Request    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Security   │ ◄── Sanitização e detecção de injeção
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Risk Analysis│ ◄── Score de risco (0-1)
└──────┬───────┘
       │
       ├─── [Risco Crítico?] ──► Handover Imediato (Nível 3)
       │
       ▼
┌──────────────┐
│     RAG      │ ◄── Busca em guias de psicologia
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Generator   │ ◄── LLM com persona "Amigo Imaginário"
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Judge     │ ◄── Validação ética
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Handover   │ ◄── Decisão final de transição
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Response   │
└──────────────┘
```

## Componentes Detalhados

### 1. Security Node

**Responsabilidade**: Primeira linha de defesa

**Funções**:
- Detecta tentativas de injeção de prompt
- Sanitiza caracteres perigosos
- Limita tamanho de mensagens
- Remove tags HTML/XML

**Padrões Detectados**:
- `ignore previous instructions`
- `you are now`
- `system:`
- Tokens especiais de modelos

### 2. Risk Analysis Node

**Responsabilidade**: Avaliação de risco de crise

**Método**:
- Análise por keywords (críticas e de alto risco)
- Detecção de padrões linguísticos
- Score de 0 a 1

**Thresholds**:
- 0.0-0.4: Baixo risco
- 0.4-0.7: Risco médio
- 0.7-0.9: Alto risco
- 0.9-1.0: Risco crítico (handover imediato)

**Keywords Críticas**:
- suicídio, me matar, quero morrer
- acabar com tudo, não vale a pena viver

### 3. RAG Engine (Subgrafo)

**Responsabilidade**: Recuperação de contexto técnico

**Stack**:
- FAISS para vector store
- OpenAI Embeddings (text-embedding-3-small)
- RecursiveCharacterTextSplitter (chunks de 1000 chars)

**Processo**:
1. Busca semântica na query do usuário
2. Retorna top-k documentos relevantes (padrão: 3)
3. Concatena contexto para o Generator

**Fontes**:
- Guias de psicologia em `data/psychology_guides/`
- Protocolos de crise
- Técnicas de escuta ativa

### 4. Generator Node

**Responsabilidade**: Geração de resposta empática

**Persona**: "Amigo Imaginário"
- Empático e acolhedor
- Não-julgador
- Validador emocional
- Pratica escuta ativa

**Diretrizes**:
- NUNCA dá diagnósticos
- NUNCA prescreve medicamentos
- SEMPRE mantém anonimato
- Encoraja ajuda profissional quando necessário

**Input**:
- System prompt com persona
- Contexto RAG
- Histórico de mensagens
- Mensagem atual

### 5. Judge Node

**Responsabilidade**: Validação ética final

**Regras** (de `ethical_policy.yaml`):
- Padrões proibidos (diagnósticos, prescrições)
- Disclaimers obrigatórios
- Validação de tom e conteúdo

**Ação em Não-Compliance**:
- Substitui resposta por mensagem segura
- Registra issues para auditoria
- Mantém transparência com usuário

### 6. Handover Subgrafo

**Responsabilidade**: Decisão de transição de nível

**Triggers**:
- Risco crítico (score >= 0.9) → Nível 3 (Profissional)
- Keywords de handover → Nível 2 (Voluntário)
- Solicitação explícita → Nível 2

**Ação**:
- Emite sinal HTTP para Gateway Go
- Payload inclui: session_id, reason, target_level, risk_score
- Gateway redireciona mensagens futuras

## Estado Compartilhado (ConversationState)

```python
{
    "session_id": str,
    "thread_id": str,
    "messages": list[dict],
    "current_message": str,
    "risk_score": float,
    "risk_factors": list[str],
    "retrieved_context": str,
    "response": str,
    "is_compliant": bool,
    "compliance_issues": list[str],
    "should_handover": bool,
    "handover_reason": str | None,
    "handover_level": int,
    "model_used": str,
    "tokens_used": int,
}
```

## Checkpointing

- **MemorySaver**: Checkpoint volátil em memória
- **Thread ID**: session_id do cliente
- **Persistência**: Zero (por design de anonimato)
- **TTL**: Sessão expira com inatividade

## Logging Seguro

**Princípio**: NUNCA logar conteúdo de mensagens

**Campos Permitidos**:
- session_id
- risk_score
- model_used
- tokens_used
- metadata

**Campos Proibidos**:
- content
- message
- response
- current_message

## Extensibilidade

### Adicionar Novo Nó

1. Criar função em `src/nodes/`
2. Assinatura: `def node(state: ConversationState) -> dict`
3. Adicionar ao grafo em `src/agents/principal.py`
4. Definir edges

### Adicionar Novo Provider LLM

1. Editar `src/llm/wrapper.py`
2. Adicionar case no `LLMFactory.create()`
3. Configurar base_url e api_key

### Customizar Política Ética

1. Editar `src/compliance/ethical_policy.yaml`
2. Adicionar padrões em `forbidden_patterns`
3. Reiniciar agent
