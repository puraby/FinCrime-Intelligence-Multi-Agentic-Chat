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

    /* ── Colour tokens ──────────────────────────────────
       bg-page      #F8FAFC  ghost white
       bg-surface   #FFFFFF  pure white cards
       bg-sidebar   #1E293B  dark slate
       accent       #10B981  emerald green
       accent-dark  #059669  emerald dark
       accent-light #D1FAE5  emerald tint
       text-primary #0F172A  near black
       text-muted   #64748B  slate 500
       border       #E2E8F0  slate 200
    ──────────────────────────────────────────────────── */

    /* ── Top bar ── */
    .topbar {
        background: #1E293B;
        padding: 13px 28px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .brand     { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 0.02em; }
    .brand-hl  { color: #10B981; }
    .pipe      { color: rgba(255,255,255,0.2); margin: 0 14px; }
    .tmode     { font-size: 13px; color: #94A3B8; }
    .user-area { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #94A3B8; }
    .avatar    {
        width: 32px; height: 32px; border-radius: 50%;
        background: #10B981;
        display: flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 700; color: #fff;
    }

    /* ── Page bg ── */
    .stApp, section.main { background: #F8FAFC !important; }

    /* ── Sidebar override ── */
    section[data-testid="stSidebar"] {
        background: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }

    /* ── Sidebar section titles ── */
    .sb-title {
        font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: #10B981 !important;
        margin: 18px 0 8px 0; padding-bottom: 5px;
        border-bottom: 1px solid #334155; display: block;
    }

    /* ── Sidebar agent cards ── */
    .agent-card {
        padding: 9px 12px; border-radius: 8px;
        border: 1px solid #334155; margin-bottom: 6px;
        background: #263448;
    }
    .agent-card-name { font-size: 13px; font-weight: 600; color: #F1F5F9 !important; }
    .agent-card-desc { font-size: 11px; color: #64748B !important; margin-top: 2px; }

    /* ── Chat bubbles ── */
    .msg-user  { display: flex; justify-content: flex-end; margin: 10px 0; }
    .msg-agent { display: flex; justify-content: flex-start; margin: 10px 0; }

    .bubble-user {
        background: #1E293B; color: #F8FAFC;
        padding: 12px 16px; border-radius: 16px 16px 4px 16px;
        max-width: 68%; font-size: 14px; line-height: 1.65;
        box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    }
    .bubble-agent {
        background: #FFFFFF; color: #0F172A;
        padding: 13px 17px; border-radius: 4px 16px 16px 16px;
        max-width: 78%; font-size: 14px; line-height: 1.7;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .bubble-agent.sar   {
        border-left: 3px solid #10B981;
        background: #F0FDF4; max-width: 90%;
    }
    .bubble-agent.table { max-width: 96%; }

    /* ── Intent badges ── */
    .intent-badge {
        display: inline-block; font-size: 10px; font-weight: 700;
        padding: 2px 9px; border-radius: 4px; margin-bottom: 8px;
        letter-spacing: 0.08em; text-transform: uppercase;
    }
    .badge-sql    { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .badge-python { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
    .badge-sar    { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
    .badge-chat   { background: #F0FDF4; color: #065F46; border: 1px solid #A7F3D0; }

    /* ── Ephemeral notice ── */
    .ephemeral-notice {
        font-size: 11px; color: #065F46; font-style: italic;
        margin-top: 7px; padding: 4px 10px;
        background: #D1FAE5; border-radius: 4px;
        border: 1px solid #6EE7B7; display: inline-block;
    }

    /* ── Empty state ── */
    .empty-chat {
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        min-height: 420px; text-align: center; gap: 14px;
        background: #F8FAFC;
    }
    .empty-icon  { font-size: 56px; opacity: 0.2; }
    .empty-title { font-size: 20px; font-weight: 700; color: #1E293B; }
    .empty-sub   {
        font-size: 14px; color: #64748B;
        max-width: 440px; line-height: 1.8;
    }
    .empty-chips {
        display: flex; flex-wrap: wrap; gap: 8px;
        justify-content: center; margin-top: 8px;
    }
    .empty-chip {
        background: #fff; border: 1px solid #E2E8F0;
        border-radius: 20px; padding: 6px 14px;
        font-size: 12px; color: #475569;
    }

    /* ── Streamlit button ── */
    div[data-testid="stButton"] > button {
        background: #1E293B !important; color: #F8FAFC !important;
        border: 1px solid #334155 !important; font-weight: 600 !important;
        border-radius: 8px !important; font-size: 13px !important;
        padding: 7px 14px !important; text-align: left !important;
        transition: background 0.15s !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #10B981 !important;
        border-color: #10B981 !important;
        color: #fff !important;
    }

    /* ── Send button ── */
    .send-btn > div[data-testid="stButton"] > button {
        background: #10B981 !important;
        border-color: #10B981 !important;
        color: #fff !important;
        text-align: center !important;
    }
    .send-btn > div[data-testid="stButton"] > button:hover {
        background: #059669 !important;
    }

    /* ── Text input ── */
    div[data-testid="stTextInput"] input {
        font-size: 15px !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 11px 16px !important;
        color: #0F172A !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16,185,129,0.12) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
    }

    /* ── Dataframe ── */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }

    /* ── Divider ── */
    hr { border-color: #E2E8F0 !important; }
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
# SIDEBAR — dark slate
# ════════════════════════════════
with sidebar:

    st.markdown('<div class="sb-title">📊 Data Queries</div>', unsafe_allow_html=True)
    for p in [
        "Show me all CRITICAL alerts",
        "Which customers have HIGH risk rating?",
        "Show alerts with offshore wires to Vanuatu",
        "How many alerts were filed this month?",
        "Top 5 alerts by risk score",
    ]:
        if st.button(p, key=f"sql_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">🔍 Investigations</div>', unsafe_allow_html=True)
    for p in [
        "Investigate ALT-2024-08821",
        "Investigate ALT-2024-08734",
        "Investigate ALT-2024-08612",
        "Investigate ALT-2024-09001",
    ]:
        if st.button(p, key=f"sar_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">🐍 Charts & Analysis</div>', unsafe_allow_html=True)
    for p in [
        "Plot alerts by risk tier as bar chart",
        "Show a pie chart of alert types",
        "Plot transaction amounts over time",
        "Calculate total amount per risk tier",
        "Show alert count by month",
    ]:
        if st.button(p, key=f"py_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">💬 AML Knowledge</div>', unsafe_allow_html=True)
    for p in [
        "What is structuring?",
        "What is the FATF grey list?",
        "Explain placement layering integration",
        "What is the CTF reporting threshold?",
        "What is Enhanced Due Diligence?",
    ]:
        if st.button(p, key=f"chat_{p}", use_container_width=True):
            st.session_state["pending_message"] = p

    st.markdown('<div class="sb-title">⚙️ Agents</div>', unsafe_allow_html=True)
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
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#334155;margin:14px 0;'>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        for k in ["chat_history","agent_history","last_chart",
                  "last_sql_data","last_sar","pending_message"]:
            st.session_state[k] = [] if k in ["chat_history","agent_history"] \
                                   else ("" if k == "pending_message" else None)
        st.rerun()

    # Session stats
    msgs = st.session_state["chat_history"]
    if msgs:
        u  = len([m for m in msgs if m["role"] == "user"])
        it = [m.get("intent","") for m in msgs if m["role"] == "assistant"]
        st.markdown(f"""
        <div style="margin-top:12px;padding:10px 12px;background:#263448;
                    border-radius:8px;border:1px solid #334155;">
          <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                      text-transform:uppercase;color:#10B981;margin-bottom:6px;">
            Session
          </div>
          <div style="font-size:12px;color:#94A3B8;line-height:1.8;">
            Messages: <b style="color:#F1F5F9;">{u}</b><br>
            SQL: <b style="color:#F1F5F9;">{it.count("sql")}</b> &nbsp;
            Charts: <b style="color:#F1F5F9;">{it.count("python")}</b> &nbsp;
            SARs: <b style="color:#F1F5F9;">{it.count("sar")}</b>
          </div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════
# MAIN CHAT
# ════════════════════════════════
with main:

    # ── Empty / welcome state ─────────────────────────────
    if not st.session_state["chat_history"]:
        st.markdown("""
        <div class="empty-chat">
          <div class="empty-icon">🤖</div>
          <div class="empty-title">FinCrime Intelligence Chat</div>
          <div class="empty-sub">
            Ask me anything about your alerts, customers, and transactions.
            I can query Delta tables, investigate alerts, generate charts,
            or answer AML/CTF compliance questions.
          </div>
          <div class="empty-chips">
            <span class="empty-chip">📊 SQL Queries</span>
            <span class="empty-chip">🔍 Alert Investigation</span>
            <span class="empty-chip">🐍 Charts & Analysis</span>
            <span class="empty-chip">💬 AML Knowledge</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Messages ──────────────────────────────────────────
    else:
        for msg in st.session_state["chat_history"]:
            role    = msg["role"]
            content = msg["content"]
            intent  = msg.get("intent", "chat")
            rtype   = msg.get("response_type", "text")

            if role == "user":
                st.markdown(f"""
                <div class="msg-user">
                  <div class="bubble-user">{content}</div>
                </div>""", unsafe_allow_html=True)

            else:
                badge_map = {
                    "sql":    ("SQL Query",   "badge-sql"),
                    "python": ("Python Code", "badge-python"),
                    "sar":    ("SAR Agent",   "badge-sar"),
                    "chat":   ("Knowledge",   "badge-chat"),
                }
                blabel, bcls = badge_map.get(intent, ("Chat", "badge-chat"))

                if rtype == "table" and msg.get("sql_data"):
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent table">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content}
                      </div>
                    </div>""", unsafe_allow_html=True)

                    df = pd.DataFrame(msg["sql_data"])
                    # Priority columns — clean table
                    priority = [
                        "alert_id","customer_id","full_name","alert_type",
                        "risk_tier","risk_score","total_amount",
                        "transaction_count","detected_at","status","sar_filed",
                        "disposition","risk_rating","kyc_tier","occupation",
                        "txn_date","amount","channel","branch",
                        "counterparty_country","fatf_status","flagged",
                        "name","bank_name","bank_country",
                    ]
                    blacklist = {
                        "assigned_to","disposition_date","model_version",
                        "notes","teller_id","atm_id","rule_id","account_id",
                        "analyst_id","analyst_notes","review_flag",
                        "history_id","alert_subtype","abn","id_number",
                        "id_type","id_expiry","segment","relationship_mgr",
                    }
                    safe = [c for c in priority if c in df.columns]
                    rest = [c for c in df.columns
                            if c not in safe and c not in blacklist]
                    final = (safe + rest)[:8]
                    st.dataframe(
                        df[final],
                        use_container_width=True,
                        height=min(120 + len(df) * 38, 380),
                        hide_index=True,
                    )
                    st.markdown(
                        '<div class="ephemeral-notice">'
                        '🔒 Generated SQL deleted after execution'
                        '</div>',
                        unsafe_allow_html=True
                    )

                elif rtype == "chart" and msg.get("chart_data"):
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content}
                      </div>
                    </div>""", unsafe_allow_html=True)
                    st.image(msg["chart_data"], use_column_width=True)
                    st.markdown(
                        '<div class="ephemeral-notice">'
                        '🔒 Generated Python code deleted after execution'
                        '</div>',
                        unsafe_allow_html=True
                    )

                elif rtype == "sar":
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent sar">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content[:500] + "..." if len(content) > 500 else content}
                      </div>
                    </div>""", unsafe_allow_html=True)

                    if msg.get("sar_result"):
                        with st.expander("📄 View Full Investigation Report"):
                            sar = msg["sar_result"]
                            c1,c2,c3,c4 = st.columns(4)
                            c1.metric("Risk Score", f"{sar.get('agent_risk_score','—')}/100")
                            c2.metric("Red Flags",  len(sar.get("red_flags") or []))
                            c3.metric("Txns",       sar.get("transaction_count","—"))
                            c4.metric("Decision",   sar.get("routing_decision","—"))
                            if sar.get("sar_narrative"):
                                st.text_area(
                                    "SAR Narrative (editable)",
                                    value=sar["sar_narrative"],
                                    height=400,
                                    key=f"sar_{id(msg)}"
                                )
                                b1, b2 = st.columns(2)
                                with b1:
                                    if st.button("✅ Approve SAR", key=f"ap_{id(msg)}"):
                                        st.success("✅ SAR approved")
                                with b2:
                                    if st.button("📤 Escalate", key=f"es_{id(msg)}"):
                                        st.warning("📤 Escalated to L2")

                else:
                    st.markdown(f"""
                    <div class="msg-agent">
                      <div class="bubble-agent">
                        <span class="intent-badge {bcls}">{blabel}</span><br>
                        {content}
                      </div>
                    </div>""", unsafe_allow_html=True)

    # ── Input bar ─────────────────────────────────────────
    st.markdown(
        "<hr style='border:none;border-top:1px solid #E2E8F0;margin:12px 0 8px 0;'>",
        unsafe_allow_html=True
    )

    inp_col, btn_col = st.columns([5.2, 0.8])

    with inp_col:
        default_val = st.session_state.get("pending_message", "")
        user_input  = st.text_input(
            "Message",
            value            = default_val,
            placeholder      = "Ask anything — query data, investigate an alert, or ask about AML...",
            label_visibility = "collapsed",
            key              = "chat_input",
        )

    with btn_col:
        with st.container():
            send = st.button("Send ➤", use_container_width=True, key="send_btn")

    # ── Process ───────────────────────────────────────────
    if (send or default_val) and user_input.strip():
        message = user_input.strip()
        st.session_state["pending_message"] = ""

        st.session_state["chat_history"].append({
            "role":    "user",
            "content": message,
        })

        with st.spinner("Agent thinking..."):
            try:
                result   = run_chat(message, st.session_state["agent_history"])
                intent   = result.get("intent", "chat")
                rtype    = result.get("response_type", "text")
                response = result.get("final_response", "No response generated.")

                amsg = {
                    "role":          "assistant",
                    "content":       response,
                    "intent":        intent,
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
                    {"role": "user",      "content": message},
                    {"role": "assistant", "content": response[:500]},
                ]
                if len(st.session_state["agent_history"]) > 20:
                    st.session_state["agent_history"] = \
                        st.session_state["agent_history"][-20:]

            except Exception as e:
                st.session_state["chat_history"].append({
                    "role":          "assistant",
                    "content":       f"Sorry, something went wrong: {str(e)}",
                    "intent":        "chat",
                    "response_type": "text",
                })

        st.rerun()