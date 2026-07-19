import duckdb

con = duckdb.connect("./.dlt/data/dev/logfire_traces.duckdb")

con.sql("""
SELECT
    trace_id,
    span_name,
    attributes__gen_ai_usage_input_tokens AS input_tokens,
    attributes__gen_ai_aggregated_usage_input_tokens AS aggregated_input_tokens
FROM agent_traces.records
WHERE trace_id IN (
    SELECT DISTINCT trace_id
    FROM agent_traces.records
    WHERE span_name = 'invoke_agent faq_agent'
)
ORDER BY trace_id, start_timestamp
""").show(max_rows=100)

con.close()

import duckdb

con = duckdb.connect("./.dlt/data/dev/logfire_traces.duckdb")

con.sql("""
SELECT
    trace_id,
    SUM(attributes__gen_ai_usage_input_tokens) AS total_input_tokens
FROM agent_traces.records
WHERE trace_id IN (
    SELECT DISTINCT trace_id
    FROM agent_traces.records
    WHERE span_name = 'invoke_agent faq_agent'
)
  AND attributes__gen_ai_usage_input_tokens IS NOT NULL
GROUP BY trace_id
ORDER BY trace_id
""").show()

con.close()