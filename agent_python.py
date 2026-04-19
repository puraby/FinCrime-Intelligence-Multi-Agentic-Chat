# ============================================================
# agent_python.py
# FinCrime Multi-Agent System — Python Agent
# ============================================================
# Generates Python code for computation and visualisation,
# executes it, captures output, then DELETES the code.
#
# Uses get_df() instead of spark.sql() — works in
# Databricks Apps without pyspark.
#
# Ephemeral execution pattern:
#   1. Generate Python code
#   2. Execute in restricted scope
#   3. Capture output / chart
#   4. DELETE generated code
#   5. Return result
# ============================================================

import io
import sys
import os
import traceback
from orchestrator import call_llm
from multi_agent_state import AgentState


# ── get_df() helper ───────────────────────────────────────
# This is injected into the exec scope so generated code
# can query Delta tables without needing pyspark

def get_df(sql_str: str):
    import pandas as pd
    from databricks import sql as dbsql
    from setup import DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH

    with dbsql.connect(
        server_hostname = DATABRICKS_HOST,
        http_path       = DATABRICKS_HTTP_PATH,
        access_token    = DATABRICKS_TOKEN,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_str)
            if cursor.description is None:
                return pd.DataFrame()
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=cols)
        
        
def agent_python(state: AgentState) -> AgentState:
    """
    Python Agent: generates and executes Python code,
    captures output, deletes the code ephemerally.
    """

    message = state["current_input"]
    print(f"\n🐍 [Python Agent] Processing: '{message[:60]}'")

    # ── Step 1: Generate Python code ─────────────────────
    print(f"   Step 1: Generating Python code...")

    code_prompt = f"""You are a Python data analyst working with financial crime data.
Generate Python code to answer the user's question.

Available functions and libraries:
- get_df(sql)  — runs SQL and returns a pandas DataFrame
  Example: df = get_df("SELECT alert_type, COUNT(*) as cnt FROM silver.alerts GROUP BY alert_type")
- plt          — matplotlib.pyplot (already imported)
- pd           — pandas (already imported)
- buf          — io.BytesIO() buffer for saving charts

Available Delta tables (schema: silver):
  silver.alerts       — alert_id, risk_tier, alert_type, risk_score, total_amount, detected_at
  silver.customers    — customer_id, full_name, risk_rating, kyc_tier, annual_income
  silver.transactions — alert_id, amount, channel, branch, counterparty_country, txn_date
  silver.alert_history — customer_id, alert_type, disposition, sar_filed
  silver.counterparties — name, bank_country, fatf_status, flagged

Rules:
- Use get_df() to fetch data — NOT spark.sql()
- For charts: use plt, call plt.tight_layout()
  then save with: plt.savefig(buf, format='png', bbox_inches='tight'); plt.close()
- For text/number results: use print() to output the answer
- Keep code simple and focused on the question
- Do NOT use display(), show(), or st.*

User question: {message}

Python code:"""

    try:
        generated_code = call_llm(code_prompt, max_tokens=700)
        generated_code = generated_code.strip()
        generated_code = generated_code.replace("```python", "").replace("```", "").strip()
        print(f"   Generated {len(generated_code)} chars of code")

    except Exception as e:
        return {
            **state,
            "final_response": f"Failed to generate code: {str(e)}",
            "response_type":  "text",
            "error":          str(e),
        }

    # ── Step 2: Execute code ──────────────────────────────
    print(f"   Step 2: Executing code...")

    # Capture stdout
    stdout_capture = io.StringIO()
    old_stdout     = sys.stdout
    sys.stdout     = stdout_capture

    chart_bytes = None
    code_error  = None

    try:
        import matplotlib
        matplotlib.use("Agg")   # non-interactive backend for server
        import matplotlib.pyplot as plt
        import pandas as pd
        import io as _io

        buf = _io.BytesIO()

        # Restricted execution scope
        # get_df is injected so generated code can query Delta tables
        exec_scope = {
            "get_df": get_df,
            "plt":    plt,
            "pd":     pd,
            "io":     _io,
            "buf":    buf,
        }

        exec(generated_code, exec_scope)

        # Check if a chart was saved to buf
        buf = exec_scope.get("buf", buf)
        if buf and buf.tell() > 0:
            buf.seek(0)
            chart_bytes = buf.read()
            print(f"Chart generated ({len(chart_bytes)} bytes)")

    except Exception:
        code_error = traceback.format_exc()
        print(f"Execution error: {code_error[:200]}")

    finally:
        sys.stdout = old_stdout

    code_output = stdout_capture.getvalue().strip()

    # ── Step 3: DELETE the generated code ────────────────
    print(f"   Step 3: Deleting generated code (ephemeral)...")
    del generated_code
    generated_code = None
    print(f"   ✅ Code deleted — no trace remains")

    # ── Step 4: Return result ─────────────────────────────
    if code_error:
        print(f"❌ [Python Agent] Execution failed")
        return {
            **state,
            "generated_code": None,
            "code_output":    code_output,
            "code_error":     code_error,
            "final_response": (
                f"Code execution failed.\n\n"
                f"Error: {code_error[:400]}\n\n"
                f"Try rephrasing your request."
            ),
            "response_type":  "text",
            "error":          code_error,
        }

    # Chart generated
    if chart_bytes:
        import streamlit as st
        st.session_state["last_chart"] = chart_bytes
        final_response = code_output or "Chart generated successfully."
        response_type  = "chart"
        print(f"✅ [Python Agent] Chart ready")

    # Text/number output
    else:
        final_response = code_output or "Code executed but produced no output. Try asking for a print() statement."
        response_type  = "text"
        print(f"✅ [Python Agent] Text output ready")

    return {
        **state,
        "generated_code": None,          # already deleted
        "code_output":    final_response,
        "code_error":     None,
        "final_response": final_response,
        "response_type":  response_type,
        "error":          None,
    }