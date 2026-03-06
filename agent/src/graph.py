"""Definição do StateGraph usando LangGraph."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from .schemas import ConversationState

# Prompt ético e acolhedor
SYSTEM_PROMPT = """Você é o AMIGO - um assistente de saúde mental empático e profissional.

DIRETRIZES ÉTICAS:
- Seja acolhedor, empático e não-julgador
- NUNCA dê diagnósticos médicos
- NUNCA substitua profissionais de saúde
- Em casos de risco iminente, sugira buscar ajuda profissional imediata
- Mantenha o anonimato total do usuário
- Foque em escuta ativa e validação emocional

QUANDO ENCAMINHAR (handover):
- Menção explícita de ideação suicida
- Crises de pânico severas
- Necessidade de diagnóstico ou medicação
- Solicitação explícita de falar com humano

Responda em português brasileiro de forma natural e acolhedora."""


def process_message(state: ConversationState) -> dict[str, Any]:
    """Nó principal: processa mensagem com LLM."""
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # Constrói histórico
    messages: list[SystemMessage | HumanMessage | AIMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in state.messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    # Adiciona mensagem atual
    messages.append(HumanMessage(content=state.current_message))

    # Invoca LLM
    response = llm.invoke(messages)
    response_text = response.content if isinstance(response.content, str) else ""

    # Detecta necessidade de handover (simplificado)
    should_handover = any(
        keyword in state.current_message.lower()
        for keyword in ["suicídio", "me matar", "quero morrer", "falar com humano"]
    )

    return {
        "response": response_text,
        "should_handover": should_handover,
        "handover_reason": "Detecção de crise ou solicitação de humano" if should_handover else None,
    }


def create_graph() -> StateGraph:
    """Cria o grafo de conversação com checkpoint em memória."""
    workflow = StateGraph(ConversationState)

    # Adiciona nó de processamento
    workflow.add_node("process", process_message)

    # Define entrada e saída
    workflow.set_entry_point("process")
    workflow.set_finish_point("process")

    # Compila com checkpoint em memória (volátil)
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
