# ============================================================
# multi_agent_state.py
# FinCrime Multi-Agent System — Shared State
# ============================================================

from typing import TypedDict, Optional, List


class AgentState(TypedDict):

    # ── Conversation history ──────────────────────────────
    # Full list of messages — grows with every turn
    # {"role": "user"/"assistant", "content": "..."}
    messages:           List[dict]

    # ── Current turn ─────────────────────────────────────
    current_input:      Optional[str]

    # ── Orchestrator decision ─────────────────────────────
    # chat / sql / python / sar
    intent:             Optional[str]
    intent_reason:      Optional[str]

    # ── SQL Agent ─────────────────────────────────────────
    generated_sql:      Optional[str]   # ephemeral — deleted after use
    sql_results:        Optional[list]
    sql_summary:        Optional[str]
    sql_columns:        Optional[list]

    # ── Python Agent ──────────────────────────────────────
    generated_code:     Optional[str]   # ephemeral — deleted after use
    code_output:        Optional[str]
    code_error:         Optional[str]

    # ── Chat Agent ────────────────────────────────────────
    chat_response:      Optional[str]

    # ── SAR Agent ─────────────────────────────────────────
    sar_alert_id:       Optional[str]
    sar_result:         Optional[dict]

    # ── Final response ────────────────────────────────────
    final_response:     Optional[str]
    response_type:      Optional[str]   # text / table / chart / sar

    # ── Error ─────────────────────────────────────────────
    error:              Optional[str]


def empty_agent_state() -> AgentState:
    """Creates a blank AgentState for a new conversation."""
    return {
        "messages":       [],
        "current_input":  None,
        "intent":         None,
        "intent_reason":  None,
        "generated_sql":  None,
        "sql_results":    None,
        "sql_summary":    None,
        "sql_columns":    None,
        "generated_code": None,
        "code_output":    None,
        "code_error":     None,
        "chat_response":  None,
        "sar_alert_id":   None,
        "sar_result":     None,
        "final_response": None,
        "response_type":  None,
        "error":          None,
    }