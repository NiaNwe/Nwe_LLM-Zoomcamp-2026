import os
from datetime import UTC, datetime, timedelta
from typing import Any, Iterator

import dlt
from dotenv import load_dotenv
from logfire.query_client import LogfireQueryClient


load_dotenv()

READ_TOKEN = os.getenv("LOGFIRE_READ_TOKEN")

if not READ_TOKEN:
    raise RuntimeError(
        "LOGFIRE_READ_TOKEN is missing. Add it to the .env file."
    )


@dlt.resource(
    name="records",
    write_disposition="replace",
)
def logfire_records() -> Iterator[dict[str, Any]]:
    """Read Logfire trace records and yield them to dlt."""

    query = """
        SELECT *
        FROM records
        ORDER BY start_timestamp
        LIMIT 10000
    """

    # Increase this period if your traces are older.
    min_timestamp = datetime.now(tz=UTC) - timedelta(days=7)

    with LogfireQueryClient(read_token=READ_TOKEN) as client:
        result = client.query_json_rows(
            sql=query,
            min_timestamp=min_timestamp,
        )

    # Current Logfire clients return {"columns": ..., "rows": ...}.
    rows = result["rows"] if isinstance(result, dict) else result

    print(f"Retrieved {len(rows)} records from Logfire")

    for row in rows:
        yield row


def run_pipeline() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire_traces",
        destination=dlt.destinations.duckdb(
            "logfire_traces.duckdb"
        ),
        dataset_name="agent_traces",
        dev_mode=False,
    )

    load_info = pipeline.run(logfire_records())
    print(load_info)


if __name__ == "__main__":
    run_pipeline()