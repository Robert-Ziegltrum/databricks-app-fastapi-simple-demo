"""Shared SQL connection utility with warehouse auto-discovery."""
import os
from functools import lru_cache
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from databricks import sql


@lru_cache(maxsize=1)
def get_http_path() -> str:
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    if warehouse_id:
        return f"/sql/1.0/warehouses/{warehouse_id}"
    try:
        w = WorkspaceClient()
        warehouses = list(w.warehouses.list())
        serverless = [wh for wh in warehouses if getattr(wh, "enable_serverless_compute", False)]
        if serverless:
            return f"/sql/1.0/warehouses/{serverless[0].id}"
        running = [wh for wh in warehouses if wh.state and wh.state.value == "RUNNING"]
        if running:
            return f"/sql/1.0/warehouses/{running[0].id}"
        if warehouses:
            return f"/sql/1.0/warehouses/{warehouses[0].id}"
    except Exception:
        pass
    raise RuntimeError("No SQL warehouse available. Set DATABRICKS_WAREHOUSE_ID in app.yaml.")


@lru_cache(maxsize=1)
def get_connection():
    cfg = Config()
    return sql.connect(
        server_hostname=cfg.host,
        http_path=get_http_path(),
        credentials_provider=lambda: cfg.authenticate,
    )


def run_query(query: str, limit: int = 1000) -> list[dict]:
    """Execute SQL and return list of dicts."""
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchmany(limit)
        cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
