# AMIGO - Assistente Mental Inteligente de Guia e Orientação

> "Ter um amigo imaginário não é sinal de loucura"  
> "Um amigo imaginário nunca vai expor seus segredos"

## Visão Geral

Plataforma de saúde mental gratuita, 24h, com foco em anonimato total e zero persistência de dados sensíveis.

## Arquitetura em 3 Níveis

1. **IA (Nível 1)**: Conversa ética com IA (Wrapper LLM)
2. **Ouvinte/Voluntário (Nível 2)**: Chat anônimo em tempo real com humanos
3. **Catálogo (Nível 3)**: Encaminhamento para profissionais

## Stack Técnica

- **Agent** (Python): Motor de IA com LangGraph
- **Backend** (Go): Gateway WebSocket e orquestrador
- **Frontend** (Next.js): Interface moderna
- **Infra**: Docker + Redis para Pub/Sub

## Início Rápido

```bash
# Subir toda a infraestrutura
docker-compose -f infra/docker-compose.yml up

# Acessar
# Frontend: http://localhost:3000
# Backend WS: ws://localhost:8080/ws
# Agent API: http://localhost:8000
```

## Princípios de Design

- **Anonimato Total**: Sem persistência de dados sensíveis
- **Segurança por Design**: Logs não registram conteúdo de mensagens
- **Modularidade**: Serviços independentes e desacoplados
