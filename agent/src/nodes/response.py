"""Response generation node with LLM."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ..core.logger import get_logger
from ..llm.wrapper import LLMFactory
from ..state.state import GraphState

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an empathetic, professional mental health support assistant.

IDENTITY:
- You are a supportive companion that never judges and always listens
- Your purpose is to offer emotional support and validation
- You are NOT a therapist, psychologist, or medical professional

CORE ETHICAL GUIDELINES:
1. NEVER provide medical diagnoses or psychiatric assessments
2. NEVER prescribe or recommend medications
3. NEVER replace professional care
4. ALWAYS maintain complete user anonymity
5. In cases of imminent risk, encourage seeking professional help

COMMUNICATION STYLE:
- Use natural, warm, and welcoming language
- Practice active listening: reflect and validate feelings
- Ask open-ended questions for better understanding
- Avoid clichés like "everything will be fine"
- Be genuine and human, not robotic

WHEN TO ESCALATE:
- Explicit suicidal ideation
- Severe panic attacks
- Need for diagnosis or medication
- Ongoing abuse or violence
- Explicit request to speak with a human

ADDITIONAL CONTEXT:
{retrieved_context}

Respond in Brazilian Portuguese in an empathetic and professional manner."""


def generator_node(state: GraphState) -> dict:
    """Response generation node using LLM."""
    logger.info("Executing generator", session_id=state["session_id"])

    # Prepare RAG context
    context = state.get("retrieved_context", "No additional context available.")

    # Create LLM
    llm = LLMFactory.create_with_fallback()

    # Build message history
    messages: list[SystemMessage | HumanMessage | AIMessage] = [
        SystemMessage(content=SYSTEM_PROMPT.format(retrieved_context=context))
    ]

    for msg in state.get("messages", []):
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    # Add current message
    messages.append(HumanMessage(content=state["current_message"]))

    # Generate response
    try:
        response = llm.invoke(messages)
        response_text = response.content if isinstance(response.content, str) else ""

        logger.info(
            "Response generated successfully",
            session_id=state["session_id"],
            model=state.get("model_used", "unknown"),
        )

        return {
            "response": response_text,
            "model_used": llm.model_name,
            "tokens_used": len(response_text.split()),  # Approximation
        }

    except Exception as e:
        logger.error(
            "Error generating response",
            session_id=state["session_id"],
            error=str(type(e).__name__),
        )
        return {
            "response": "Sorry, I'm experiencing technical difficulties. Can you try again?",
            "model_used": "fallback",
            "tokens_used": 0,
        }
