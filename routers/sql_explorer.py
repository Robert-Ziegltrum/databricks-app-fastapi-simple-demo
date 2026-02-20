"""Ad-hoc SQL explorer endpoint."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.sql_client import run_query

router = APIRouter(prefix="/api/v1/sql", tags=["sql"])

BLOCKED = ["insert", "update", "delete", "drop", "create", "alter", "truncate", "merge"]


class QueryRequest(BaseModel):
    query: str
    max_rows: int = 500


@router.post("/run")
async def run_sql(body: QueryRequest):
    q = body.query.strip().rstrip(";")
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Block write statements
    first_word = q.split()[0].lower() if q.split() else ""
    if first_word in BLOCKED:
        raise HTTPException(status_code=400, detail=f"Statement type '{first_word}' is not allowed.")

    # Wrap in limit if needed
    if "limit" not in q.lower():
        q = f"SELECT * FROM ({q}) _q LIMIT {min(body.max_rows, 5000)}"

    try:
        rows = run_query(q, limit=min(body.max_rows, 5000))
        columns = list(rows[0].keys()) if rows else []
        return {"columns": columns, "rows": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
