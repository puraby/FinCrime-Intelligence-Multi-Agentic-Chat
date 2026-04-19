# ============================================================
# orchestrator.py
# FinCrime Multi-Agent System — Orchestrator
# ============================================================
# Reads the analyst message and classifies intent.
# Routes to the correct agent.
#
# Intent types:
#   sql     → data query against Delta tables
#   python  → computation or visualisation
#   sar     → investigate a specific alert
#   chat    → general AML/CTF knowledge question
# ============================================================

import re
import requests
import os
from setup import DATABRICKS_HOST, DATABRICKS_TOKEN
from multi_agent_state import AgentState

# ── Model config ──────────────────────────────────────────
GATEWAY = "https://7474647235375729.ai-gateway.cloud.databricks.com/mlflow/v1/chat/completions"
MODEL   = "databricks-meta-llama-3-3-70b-instruct"


def get_token() -> str:
    """Get OAuth token for gateway calls."""
    client_id     = os.environ.get("DATABRICKS_CLIENT_ID", "")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET", "")
    if not client_id:
        return DATABRICKS_TOKEN
    response = requests.post(
        f"https://{DATABRICKS_HOST}/oidc/v1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type":    "client_credentials",
            "client_id":     client_id,
            "client_secret": client_secret,
            "scope":         "all-apis",
        }
    )
    return response.json().get("access_token", DATABRICKS_TOKEN) \
           if response.status_code == 200 else DATABRICKS_TOKEN


def call_llm(prompt: str, max_tokens: int = 200) -> str:
    """Call the LLM gateway."""
    token = get_token()
    response = requests.post(
        GATEWAY,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        },
        json={
            "model":      MODEL,
            "max_tokens": max_tokens,
            "messages":   [{"role": "user", "content": prompt}],
        },
        timeout=60
    )
    if response.status_code != 200:
        raise RuntimeError(f"LLM error {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"].strip()


def orchestrator(state: AgentState) -> AgentState:
    """
    Reads the analyst message and classifies intent.
    Sets state["intent"] to one of: sql / python / sar / chat
    """

    message = state["current_input"]
    print(f"\n🎯 [Orchestrator] Classifying: '{message[:60]}...' " 
          if len(message) > 60 else f"\n🎯 [Orchestrator] Classifying: '{message}'")

    # ── Rule-based pre-classification ─────────────────────
    # Fast classification without LLM for obvious cases
    msg_lower = message.lower()

    # SAR investigation — detect alert ID pattern
    alert_id_match = re.search(r'ALT-\d{4}-\d{5}', message, re.IGNORECASE)
    if alert_id_match or any(w in msg_lower for w in
                              ["investigate", "draft sar", "run agent",
                               "file sar", "suspicious matter"]):
        alert_id = alert_id_match.group(0) if alert_id_match else None
        print(f"✅ [Orchestrator] Intent: SAR (rule-based)")
        print(f"   Alert ID: {alert_id}")
        return {
            **state,
            "intent":        "sar",
            "intent_reason": "Alert ID detected or investigation keyword found",
            "sar_alert_id":  alert_id,
            "error":         None,
        }

    # Python/visualisation — detect chart/plot keywords
    if any(w in msg_lower for w in
           ["plot", "chart", "graph", "visualise", "visualize",
            "histogram", "bar chart", "pie chart", "heatmap",
            "calculate", "compute", "percentage", "rate"]):
        print(f"✅ [Orchestrator] Intent: PYTHON (rule-based)")
        return {
            **state,
            "intent":        "python",
            "intent_reason": "Visualisation or computation keyword detected",
            "error":         None,
        }

    # SQL — detect data query keywords
    if any(w in msg_lower for w in
           ["show me", "list", "find", "how many", "which",
            "filter", "select", "count", "top", "all alerts",
            "all customers", "transactions", "where", "fetch"]):
        print(f"✅ [Orchestrator] Intent: SQL (rule-based)")
        return {
            **state,
            "intent":        "sql",
            "intent_reason": "Data query keyword detected",
            "error":         None,
        }

    # ── LLM classification for ambiguous messages ─────────
    print(f"   Rule-based inconclusive — asking LLM...")

    # Build conversation context for better classification
    recent = state.get("messages", [])[-4:]  # last 4 messages
    context = "\n".join(
        f"{m['role'].upper()}: {m['content'][:100]}"
        for m in recent
    )

    prompt = f"""You are an intent classifier for an AML compliance chatbot.

Classify the user message into exactly one of these intents:
  sql     - User wants to query data from the database (alerts, customers, transactions)
  python  - User wants a chart, visualisation, or computation
  sar     - User wants to investigate a specific alert or draft a SAR
  chat    - User wants to know about AML concepts, regulations, or general questions

Recent conversation:
{context}

Current message: "{message}"

Reply with ONLY one word: sql, python, sar, or chat"""

    try:
        intent = call_llm(prompt, max_tokens=10).lower().strip()
        # Clean up — extract just the intent word
        for valid in ["sql", "python", "sar", "chat"]:
            if valid in intent:
                intent = valid
                break
        else:
            intent = "chat"  # default fallback

        print(f"✅ [Orchestrator] Intent: {intent.upper()} (LLM)")
        return {
            **state,
            "intent":        intent,
            "intent_reason": "LLM classification",
            "error":         None,
        }

    except Exception as e:
        print(f"⚠️  [Orchestrator] LLM failed — defaulting to chat: {e}")
        return {
            **state,
            "intent":        "chat",
            "intent_reason": "Fallback — LLM unavailable",
            "error":         None,
        }