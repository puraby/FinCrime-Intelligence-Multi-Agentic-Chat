# ============================================================
# agent_chat.py
# FinCrime Multi-Agent System — Chat Agent
# ============================================================
# Answers general AML/CTF knowledge questions.
# No database queries — pure LLM with domain knowledge.
#
# Examples:
#   "What is structuring?"
#   "What does FATF grey list mean?"
#   "What is the CTF reporting threshold in Australia?"
#   "Explain the placement layering integration model"
# ============================================================

from orchestrator import call_llm
from multi_agent_state import AgentState


# ── AML/CTF System Prompt ─────────────────────────────────
# This gives the LLM its persona and domain knowledge context
SYSTEM_PROMPT = """You are an expert AML/CTF compliance analyst at 
Commonwealth Bank of Australia (CBA).

You have deep expertise in:
- Australian AML/CTF Act 2006 and AUSTRAC regulations
- FATF recommendations and grey/black lists
- Financial crime typologies (structuring, smurfing, layering, 
  trade-based ML, crypto ML, PEP risk)
- Suspicious Matter Report (SMR) filing obligations
- Customer Due Diligence (CDD) and Enhanced Due Diligence (EDD)
- CTF reporting thresholds ($10,000 AUD cash transaction reports)
- Correspondent banking and SWIFT wire risk

Answer questions clearly and precisely.
Reference specific legislation and AUSTRAC guidance where relevant.
Keep answers concise but complete.
If asked about specific customer data, explain you need an Alert ID
to investigate — suggest using format ALT-YYYY-NNNNN."""


def agent_chat(state: AgentState) -> AgentState:
    """
    Chat Agent: answers AML/CTF knowledge questions.
    Uses conversation history for context-aware responses.
    """

    message = state["current_input"]
    print(f"\n💬 [Chat Agent] Answering: '{message[:60]}'")

    # ── Build messages with history ───────────────────────
    # Include last 6 messages for conversation context
    history  = state.get("messages", [])[-6:]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history[:-1]:  # all but current
        messages.append({
            "role":    msg["role"],
            "content": msg["content"]
        })

    messages.append({"role": "user", "content": message})

    # ── Call LLM ─────────────────────────────────────────
    try:
        from orchestrator import get_token, GATEWAY, MODEL
        import requests

        token = get_token()
        response = requests.post(
            GATEWAY,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
            json={
                "model":      MODEL,
                "max_tokens": 800,
                "messages":   messages,
            },
            timeout=60
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Gateway error {response.status_code}: {response.text[:200]}"
            )

        answer = response.json()["choices"][0]["message"]["content"].strip()
        print(f"✅ [Chat Agent] Response generated ({len(answer.split())} words)")

        return {
            **state,
            "chat_response": answer,
            "final_response": answer,
            "response_type": "text",
            "error":         None,
        }

    except Exception as e:
        error_msg = f"Chat agent error: {str(e)}"
        print(f"❌ [Chat Agent] {error_msg}")
        return {
            **state,
            "chat_response":  None,
            "final_response": "I encountered an error. Please try again.",
            "response_type":  "text",
            "error":          error_msg,
        }