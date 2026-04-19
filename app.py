import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_agent_graph import run_chat

st.set_page_config(
    page_title="FinCrime Intelligence Chat",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ── Deep Amber Theme ───────────────────────────── */
    .stApp, section.main {
        background: #F6F1EA !important;
    }

    /* ── Top bar ── */
    .topbar {
        background: #FBF7F2;
        padding: 16px 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #E5D9CC;
    }
    .brand {
        font-size: 17px;
        font-weight: 700;
        color: #201A17;
        letter-spacing: 0.01em;
    }
    .brand-hl { color: #A14C10; }
    .pipe { color: #CBBFB3; margin: 0 14px; }
    .tmode { font-size: 13px; color: #8B7C73; }
    .user-area {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 13px;
        color: #6D625B;
    }
    .avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: #A14C10;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: #fff;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #F3ECE3 !important;
        border-right: 1px solid #E5D9CC !important;
    }
    section[data-testid="stSidebar"] * {
        color: #3E342E !important;
    }

    .sb-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #A14C10 !important;
        margin: 18px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #D8CDBF;
        display: block;
    }

    .agent-card {
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid #E5D9CC;
        margin-bottom: 8px;
        background: #FBF7F2;
    }
    .agent-card-name {
        font-size: 13px;
        font-weight: 600;
        color: #201A17 !important;
    }
    .agent-card-desc {
        font-size: 11px;
        color: #7B6D64 !important;
        margin-top: 3px;
    }

    /* ── Message wrappers ── */
    .msg-user  { display: flex; justify-content: flex-end; margin: 10px 0; }
    .msg-agent { display: flex; justify-content: flex-start; margin: 10px 0; }

    /* ── Chat bubbles ── */
    .bubble-user {
        background: #1F1A17;
        color: #FFFDF9;
        padding: 12px 16px;
        border-radius: 16px 16px 6px 16px;
        max-width: 68%;
        font-size: 14px;
        line-height: 1.65;
        box-shadow: none;
    }
    .bubble-agent {
        background: #FBF7F2;
        color: #201A17;
        padding: 13px 17px;
        border-radius: 6px 16px 16px 16px;
        max-width: 78%;
        font-size: 14px;
        line-height: 1.7;
        border: 1px solid #E5D9CC;
        box-shadow: none;
    }
    .bubble-agent.sar {
        border-left: 3px solid #A14C10;
        background: #FBF7F2;
        max-width: 90%;
    }
    .bubble-agent.table {
        max-width: 96%;
    }

    /* ── Intent badges ── */
    .intent-badge {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: #F3E3D3;
        color: #A14C10;
        border: 1px solid #E7C9A1;
    }
    .badge-sql,
    .badge-python,
    .badge-sar,
    .badge-chat {
        background: #F3E3D3;
        color: #A14C10;
        border: 1px solid #E7C9A1;
    }

    /* ── Ephemeral notice ── */
    .ephemeral-notice {
        font-size: 11px;
        color: #6B625C;
        font-style: italic;
        margin-top: 7px;
        padding: 5px 10px;
        background: #F5F1EA;
        border-radius: 8px;
        border: 1px solid #E5D9CC;
        display: inline-block;
    }

    /* ── Empty state ── */
    .empty-chat {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 420px;
        text-align: center;
        gap: 14px;
        background: #F6F1EA;
    }
    .empty-icon  {
        font-size: 56px;
        opacity: 0.22;
    }
    .empty-title {
        font-size: 20px;
        font-weight: 700;
        color: #201A17;
    }
    .empty-sub {
        font-size: 14px;
        color: #7B6D64;
        max-width: 460px;
        line-height: 1.8;
    }
    .empty-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-top: 8px;
    }
    .empty-chip {
        background: #FBF7F2;
        border: 1px solid #E5D9CC;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        color: #5E524B;
    }

    /* ── Buttons ── */
    div[data-testid="stButton"] > button {
        background: #FBF7F2 !important;
        color: #3A2F29 !important;
        border: 1px solid #E0D4C6 !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        font-size: 13px !important;
        padding: 10px 14px !important;
        text-align: left !important;
        box-shadow: none !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #F7EEDC !important;
        border-color: #D6B98F !important;
        color: #A14C10 !important;
    }

    /* ── Send button ── */
    .send-btn div[data-testid="stButton"] > button,
    div[data-testid="stButton"] > button[kind="secondary"] {
        text-align: center !important;
    }

    /* ── Text input ── */
    div[data-testid="stTextInput"] input {
        font-size: 15px !important;
        border: 1.5px solid #E5D9CC !important;
        border-radius: 12px !important;
        padding: 11px 16px !important;
        color: #201A17 !important;
        background: #FBF7F2 !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #D6B98F !important;
        box-shadow: 0 0 0 2px rgba(161, 76, 16, 0.08) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #9A8E84 !important;
    }

    /* ── Dataframe ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E5D9CC !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: none !important;
        background: #FBF7F2 !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #E5D9CC !important;
    }

    /* ── Metrics and expanders ── */
    div[data-testid="stMetric"] {
        background: #FBF7F2;
        border: 1px solid #E5D9CC;
        padding: 10px;
        border-radius: 12px;
    }

    details {
        background: #FBF7F2;
        border: 1px solid #E5D9CC;
        border-radius: 12px;
        padding: 6px 10px;
    }

</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────
for key, default in [
    ("chat_history",   []),
    ("agent_history",  []),
    ("last_chart",     None),
    ("last_sql_data",  None),
    ("last_sar",       None),
    ("pending_message", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Top bar ───────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div style="display:flex;align-items:center;">
    <div class="brand">
      <span class="brand-hl">FinCrime</span> Intelligence
    </div>
    <div class="pipe">|</div>
    <div class="tmode">Multi-Agent Chat</div>
  </div>
  <div class="user-area">
    <div class="avatar">PD</div>
    Puraby Dev
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────
sidebar, main = st.columns([1, 3])

# ════════════════════════════════
# SIDEBAR
# ════════════════════════════════
with sidebar:

    st.markdown('<div class="sb-title">Data Queries</div>', unsafe_allow_html=True)
    for p in [
        "Show me all CRITICAL alerts",
        "Top 5 alerts by risk score",
    ]:
        if st.button(p, key=f"sql_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">Investigations</div>', unsafe_allow_html=True)
    for p in [
        "Investigate ALT-2024-08821",
        "Investigate ALT-2024-08612",
    ]:
        if st.button(p, key=f"sar_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">Charts & Analysis</div>', unsafe_allow_html=True)
    for p in [
        "Plot alerts by risk tier as bar chart",
        "Calculate total amount per risk tier",
    ]:
        if st.button(p, key=f"py_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">AML Knowledge</div>', unsafe_allow_html=True)
    for p in [
        "What is structuring?",
        "What is Enhanced Due Diligence?",
    ]:
        if st.button(p, key=f"chat_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">Agents</div>', unsafe_allow_html=True)
    for icon, name, desc in [
        ("💬", "Chat Agent",   "AML/CTF knowledge Q&A"),
        ("🔍", "SQL Agent",    "NL → SQL → Delta tables"),
        ("🐍", "Python Agent", "Charts & computation"),
        ("📝", "SAR Agent",    "Alert investigation"),
    ]:
        st.markdown(f"""
        <div class="agent-card">
          <div class="agent-card-name">{icon} {name}</div>
          <div class="agent-card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)

    if st.button("Clear Conversation", use_container_width=True):
        for k in ["chat_history", "agent_history", "last_chart",
                  "last_sql_data", "last_sar", "pending_message"]:
            st.session_state[k] = [] if k in ["chat_history", "agent_history"] \
                else ("" if k == "pending_message" else None)
        st.rerun()

    msgs = st.session_state["chat_history"]
    if msgs:
        user_messages = len([m for m in msgs if m["role"] == "user"])
        intents = [m.get("intent", "") for m in msgs if m["role"] == "assistant"]

        st.markdown(f"""
        <div style="
            margin-top:12px;
            padding:12px;
            background:#FBF7F2;
            border-radius:12px;
            border:1px solid #E5D9CC;
        ">
          <div style="
              font-size:10px;
              font-weight:700;
              letter-spacing:0.1em;
              text-transform:uppercase;
              color:#A14C10;
              margin-bottom:6px;
          ">
            Session
          </div>
          <div style="font-size:12px;color:#6D625B;line-height:1.8;">
            Messages: <b style="color:#201A17;">{user_messages}</b><br>
            SQL: <b style="color:#201A17;">{intents.count("sql")}</b> &nbsp;
            Charts: <b style="color:#201A17;">{intents.count("python")}</b> &nbsp;
            SARs: <b style="color:#201A17;">{intents.count("sar")}</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════
# MAIN CHAT
# ════════════════════════════════
with main:

    if not st.session_state["chat_history"]:
        st.markdown("""
        <div class="empty-chat">
          <div class="empty-icon">🏦</div>
          <div class="empty-title">FinCrime Intelligence Chat</div>
          <div class="empty-sub">
            Ask me about alerts, customers, transactions, investigations, or AML concepts.
            I can query Delta tables, investigate alerts, generate charts, and draft SAR outputs.
          </div>
          <div class="empty-chips">
            <span class="empty-chip">SQL Queries</span>
            <span class="empty-chip">Alert Investigation</span>
            <span class="empty-chip">Charts & Analysis</span>
            <span class="empty-chip">AML Knowledge</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        for msg in st.session_state["chat_history"]:
            role = msg["role"]
            content = msg["content"]
            intent = msg.get("intent", "chat")
            rtype = msg.get("response_type", "text")

            if role == "user":
                st.markdown(f"""
                <div class="msg-user">
                  <div class="bubble-user">{content}</div>
                </div>
                """, unsafe_allow_html=True)

            else:
                badge_map = {
                    "sql":    ("SQL Query", "badge-sql"),
                    "python": ("Python Agent", "badge-python"),
                    "sar":    ("SAR Agent", "badge-sar"),
                    "chat":   ("Knowledge", "badge-chat"),
                }
                blabel, bcls = badge_map.get(intent, ("Chat", "badge-chat"))

                if rtype == "table" and msg.get("sql_data"):
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent table">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    df = pd.DataFrame(msg["sql_data"])
                    priority = [
                        "alert_id", "customer_id", "full_name", "alert_type",
                        "risk_tier", "risk_score", "total_amount",
                        "transaction_count", "detected_at", "status", "sar_filed",
                        "disposition", "risk_rating", "kyc_tier", "occupation",
                        "txn_date", "amount", "channel", "branch",
                        "counterparty_country", "fatf_status", "flagged",
                        "name", "bank_name", "bank_country",
                    ]
                    blacklist = {
                        "assigned_to", "disposition_date", "model_version",
                        "notes", "teller_id", "atm_id", "rule_id", "account_id",
                        "analyst_id", "analyst_notes", "review_flag",
                        "history_id", "alert_subtype", "abn", "id_number",
                        "id_type", "id_expiry", "segment", "relationship_mgr",
                    }

                    safe = [c for c in priority if c in df.columns]
                    rest = [c for c in df.columns if c not in safe and c not in blacklist]
                    final = (safe + rest)[:8]

                    st.dataframe(
                        df[final],
                        use_container_width=True,
                        height=min(120 + len(df) * 38, 380),
                        hide_index=True,
                    )

                    st.markdown(
                        '<div class="ephemeral-notice">Generated SQL deleted after execution</div>',
                        unsafe_allow_html=True
                    )

                elif rtype == "chart" and msg.get("chart_data"):
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.image(msg["chart_data"], use_column_width=True)

                    st.markdown(
                        '<div class="ephemeral-notice">Generated Python code deleted after execution</div>',
                        unsafe_allow_html=True
                    )

                elif rtype == "sar":
                    display_text = content[:500] + "..." if len(content) > 500 else content
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent sar">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {display_text}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if msg.get("sar_result"):
                        with st.expander("View Full Investigation Report"):
                            sar = msg["sar_result"]
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("Risk Score", f"{sar.get('agent_risk_score', '—')}/100")
                            c2.metric("Red Flags", len(sar.get("red_flags") or []))
                            c3.metric("Txns", sar.get("transaction_count", "—"))
                            c4.metric("Decision", sar.get("routing_decision", "—"))

                            if sar.get("sar_narrative"):
                                st.text_area(
                                    "SAR Narrative (editable)",
                                    value=sar["sar_narrative"],
                                    height=400,
                                    key=f"sar_{id(msg)}"
                                )
                                b1, b2 = st.columns(2)
                                with b1:
                                    if st.button("Approve SAR", key=f"ap_{id(msg)}"):
                                        st.success("SAR approved")
                                with b2:
                                    if st.button("Escalate", key=f"es_{id(msg)}"):
                                        st.warning("Escalated to L2")

                else:
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown(
        "<hr style='border:none;border-top:1px solid #E5D9CC;margin:12px 0 8px 0;'>",
        unsafe_allow_html=True
    )

    inp_col, btn_col = st.columns([5.2, 0.8])

    with inp_col:
        default_val = st.session_state.get("pending_message", "")
        user_input = st.text_input(
            "Message",
            value=default_val,
            placeholder="Ask about alerts, investigations, charts, or AML knowledge...",
            label_visibility="collapsed",
            key="chat_input",
        )

    with btn_col:
        send = st.button("Send", use_container_width=True, key="send_btn")

    if (send or default_val) and user_input.strip():
        message = user_input.strip()
        st.session_state["pending_message"] = ""

        st.session_state["chat_history"].append({
            "role": "user",
            "content": message,
        })

        with st.spinner("Agent thinking..."):
            try:
                result = run_chat(message, st.session_state["agent_history"])
                intent = result.get("intent", "chat")
                rtype = result.get("response_type", "text")
                response = result.get("final_response", "No response generated.")

                amsg = {
                    "role": "assistant",
                    "content": response,
                    "intent": intent,
                    "response_type": rtype,
                }

                if rtype == "table":
                    amsg["sql_data"] = result.get("sql_results")
                if rtype == "chart":
                    amsg["chart_data"] = st.session_state.get("last_chart")
                if rtype == "sar":
                    amsg["sar_result"] = result.get("sar_result")

                st.session_state["chat_history"].append(amsg)

                st.session_state["agent_history"] += [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response[:500]},
                ]

                if len(st.session_state["agent_history"]) > 20:
                    st.session_state["agent_history"] = st.session_state["agent_history"][-20:]

            except Exception as e:
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": f"Sorry, something went wrong: {str(e)}",
                    "intent": "chat",
                    "response_type": "text",
                })

        st.rerun()