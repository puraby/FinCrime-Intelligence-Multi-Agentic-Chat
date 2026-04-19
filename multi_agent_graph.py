# ============================================================
# multi_agent_graph.py
# FinCrime Multi-Agent System — LangGraph Orchestration
# ============================================================
# Wires orchestrator + 4 agents into a LangGraph graph.
#
#  START
#    │
#    ▼
#  orchestrator  (classifies intent)
#    │
#    ├── sql    ──► agent_sql    ──► END
#    ├── python ──► agent_python ──► END
#    ├── sar    ──► agent_sar    ──► END  ← ephemeral
#    └── chat   ──► agent_chat   ──► END
#
# Note: agent_sar is now fully ephemeral — no node files,
# no graph.py. Generates code on the fly, executes,
# deletes everything, returns SAR.
# ============================================================

from langgraph.graph import StateGraph, END
from multi_agent_state import AgentState, empty_agent_state
from orchestrator  import orchestrator
from agent_chat    import agent_chat
from agent_sql     import agent_sql
from agent_python  import agent_python
from agent_sar     import agent_sar          # ← new ephemeral SAR agent


# ── Routing function ──────────────────────────────────────
def route_to_agent(state: AgentState) -> str:
    intent = state.get("intent", "chat")
    print(f"🔀 [Router] Routing to: {intent.upper()}")
    return intent


# ── Build graph ───────────────────────────────────────────
def build_multi_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator",  orchestrator)
    graph.add_node("agent_chat",    agent_chat)
    graph.add_node("agent_sql",     agent_sql)
    graph.add_node("agent_python",  agent_python)
    graph.add_node("agent_sar",     agent_sar)

    graph.set_entry_point("orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        route_to_agent,
        {
            "chat":   "agent_chat",
            "sql":    "agent_sql",
            "python": "agent_python",
            "sar":    "agent_sar",
        }
    )

    graph.add_edge("agent_chat",   END)
    graph.add_edge("agent_sql",    END)
    graph.add_edge("agent_python", END)
    graph.add_edge("agent_sar",    END)

    return graph.compile()


# ── run_chat() ────────────────────────────────────────────
def run_chat(message: str, history: list) -> AgentState:
    """
    Main entry point for the chatbot.

    Usage:
        result = run_chat("Investigate ALT-2024-08821", history)
        print(result["final_response"])
    """
    multi_graph = build_multi_agent_graph()

    state = empty_agent_state()
    state["messages"]      = history + [{"role": "user", "content": message}]
    state["current_input"] = message

    return multi_graph.invoke(state)


print("✅ multi_agent_graph.py loaded")
print("   Agents: chat | sql | python | sar (ephemeral)")
print("   run_chat(message, history) → ready")