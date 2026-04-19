# ============================================================
# agent_sql.py
# FinCrime Multi-Agent System — SQL Agent
# ============================================================
# Converts natural language to SQL, executes against
# Delta tables via Databricks SQL Connector,
# summarises results, then DELETES the SQL.
#
# Ephemeral execution pattern:
#   1. Generate SQL (never SELECT *)
#   2. Execute via SQL Connector
#   3. DELETE generated SQL from memory
#   4. Summarise results in plain English
# ============================================================

import os
from orchestrator import call_llm
from multi_agent_state import AgentState
from databricks import sql as dbsql


# ── Connection helper ─────────────────────────────────────
def get_connection():
    """Get Databricks SQL Connector connection."""
    from setup import DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH
    return dbsql.connect(
        server_hostname = DATABRICKS_HOST,
        http_path       = DATABRICKS_HTTP_PATH,
        access_token    = DATABRICKS_TOKEN,
    )


# ── Table schema ──────────────────────────────────────────
# Only include columns that are safe to query.
# Deliberately excludes null columns like assigned_to,
# disposition (in alerts), model_version — these cause
# Spark resolution errors when selected.

SCHEMA_CONTEXT = """
Available Delta tables (schema: silver):

silver.alerts
  alert_id          STRING   -- e.g. ALT-2024-08821
  customer_id       STRING   -- e.g. CUS-10042
  rule_id           STRING
  rule_name         STRING   -- e.g. STRUCT_THRESHOLD_AVOID
  alert_type        STRING   -- e.g. Structuring, Velocity
  alert_subtype     STRING
  risk_score        INT      -- 0 to 100
  risk_tier         STRING   -- LOW, MEDIUM, HIGH, CRITICAL
  total_amount      DOUBLE
  transaction_count INT
  period_start      DATE
  period_end        DATE
  detected_at       TIMESTAMP
  status            STRING   -- OPEN, CLOSED
  sar_filed         BOOLEAN
  notes             STRING

silver.customers
  customer_id       STRING
  full_name         STRING
  dob               DATE
  occupation        STRING
  employer          STRING
  annual_income     DOUBLE
  address           STRING
  state             STRING
  customer_since    DATE
  kyc_tier          STRING   -- STANDARD, ENHANCED
  risk_rating       STRING   -- LOW, MEDIUM, HIGH
  pep_flag          BOOLEAN
  fatca_flag        BOOLEAN

silver.accounts
  account_id         STRING
  customer_id        STRING
  bsb                STRING
  account_number     STRING
  account_type       STRING
  avg_monthly_credit DOUBLE
  avg_monthly_debit  DOUBLE

silver.transactions
  txn_id               STRING
  alert_id             STRING
  customer_id          STRING
  txn_date             DATE
  amount               DOUBLE
  channel              STRING   -- CASH_DEPOSIT, SWIFT_OUTWARD, DIRECT_CREDIT
  direction            STRING   -- CREDIT, DEBIT
  branch               STRING
  counterparty_country STRING   -- ISO code e.g. VU, PH, AU
  reference            STRING

silver.alert_history
  history_id        STRING
  customer_id       STRING
  alert_id          STRING
  alert_date        DATE
  alert_type        STRING
  risk_score        INT
  disposition       STRING   -- FALSE_POSITIVE, SAR_FILED, CLOSED_NO_ACTION
  sar_filed         BOOLEAN

silver.counterparties
  counterparty_id      STRING
  name                 STRING
  bank_name            STRING
  bank_country         STRING   -- ISO code
  fatf_status          STRING   -- STANDARD, GREY_LIST, BLACK_LIST
  flagged              BOOLEAN
  relationship_to_cust STRING
"""


def agent_sql(state: AgentState) -> AgentState:
    """
    SQL Agent: natural language → SQL → execute → delete → summarise.
    """

    message = state["current_input"]
    print(f"\n🔍 [SQL Agent] Processing: '{message[:60]}'")

    # ── Step 1: Generate SQL ──────────────────────────────
    print(f"   Step 1: Generating SQL...")

    sql_prompt = f"""You are a SQL expert for Databricks Delta Lake.
Convert the user question to a valid SQL query.

{SCHEMA_CONTEXT}

STRICT RULES — follow every rule exactly:
- NEVER use SELECT * — always list specific column names explicitly
- Only use columns that exist in the schema above — no other columns
- Use fully qualified table names: silver.alerts, silver.customers etc.
- Always add ORDER BY for meaningful sorting
- Limit results to 50 rows max using LIMIT 50
- Use CURRENT_DATE() for today's date
- For date arithmetic use: DATE_SUB(CURRENT_DATE(), 30) for last 30 days
- For joins always use explicit JOIN ... ON syntax
- Return ONLY the SQL query — no explanation, no markdown, no backticks

Example of correct query:
SELECT alert_id, customer_id, alert_type, risk_tier, risk_score, total_amount, detected_at
FROM silver.alerts
WHERE risk_tier = 'CRITICAL'
ORDER BY risk_score DESC
LIMIT 50

User question: {message}

SQL:"""

    try:
        generated_sql = call_llm(sql_prompt, max_tokens=500)
        generated_sql = generated_sql.strip()
        # Clean any markdown the LLM might add
        generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
        # Remove any leading/trailing whitespace or newlines
        generated_sql = "\n".join(
            line for line in generated_sql.splitlines()
            if line.strip()
        )
        print(f"   SQL generated:\n   {generated_sql[:200]}")

    except Exception as e:
        return {
            **state,
            "final_response": f"Failed to generate SQL: {str(e)}",
            "response_type":  "text",
            "error":          str(e),
        }

    # ── Step 2: Execute via SQL Connector ─────────────────
    print(f"\n   Step 2: Executing against Delta tables...")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(generated_sql)
                if cursor.description is None:
                    results   = []
                    cols      = []
                    row_count = 0
                else:
                    cols      = [d[0] for d in cursor.description]
                    rows      = cursor.fetchall()
                    results   = [dict(zip(cols, row)) for row in rows]
                    row_count = len(results)

        print(f"   ✅ Executed — {row_count} rows returned")

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Execution failed: {error_msg[:150]}")

        # Delete SQL even on failure — ephemeral
        del generated_sql
        generated_sql = None

        return {
            **state,
            "generated_sql":  None,
            "final_response": (
                f"Query failed to execute.\n\n"
                f"Error: {error_msg[:300]}\n\n"
                f"Try rephrasing your question more specifically."
            ),
            "response_type":  "text",
            "error":          error_msg,
        }

    # ── Step 3: DELETE the generated SQL ─────────────────
    print(f"\n   Step 3: Deleting generated SQL (ephemeral)...")
    del generated_sql
    generated_sql = None
    print(f"   ✅ SQL deleted — no trace remains")

    # ── Step 4: Summarise results ─────────────────────────
    print(f"\n   Step 4: Summarising {row_count} results...")

    if row_count == 0:
        summary = (
            "No results found. The query returned 0 rows. "
            "Try broadening your search criteria."
        )
    else:
        sample      = results[:10]
        result_text = "\n".join(str(row) for row in sample)

        summary_prompt = f"""You are an AML compliance analyst.
Summarise these database query results in 2-3 clear sentences.
Focus on what is most relevant for financial crime investigation.
Be specific with numbers, names, and key findings.

Original question: {message}
Total rows returned: {row_count}
Sample results (first 10 of {row_count}):
{result_text}

Summary:"""

        try:
            summary = call_llm(summary_prompt, max_tokens=250)
        except Exception:
            summary = f"Query returned {row_count} record(s). See table below for full details."

    print(f"✅ [SQL Agent] Complete — {row_count} rows, summary ready")

    return {
        **state,
        "generated_sql":  None,        # already deleted
        "sql_results":    results,
        "sql_columns":    cols,
        "sql_summary":    summary,
        "final_response": summary,
        "response_type":  "table",
        "error":          None,
    }