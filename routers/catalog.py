"""Unity Catalog browser endpoints."""
from fastapi import APIRouter, HTTPException
from functools import lru_cache
from databricks.sdk import WorkspaceClient

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


@lru_cache(maxsize=1)
def _client():
    return WorkspaceClient()


@router.get("/catalogs")
async def list_catalogs():
    try:
        w = _client()
        catalogs = [c.name for c in w.catalogs.list() if c.name]
        # Surface samples first
        if "samples" in catalogs:
            catalogs = ["samples"] + [c for c in catalogs if c != "samples"]
        return {"catalogs": catalogs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemas/{catalog}")
async def list_schemas(catalog: str):
    try:
        w = _client()
        schemas = [s.name for s in w.schemas.list(catalog_name=catalog) if s.name]
        return {"schemas": schemas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{catalog}/{schema}")
async def list_tables(catalog: str, schema: str):
    try:
        w = _client()
        tables = [
            {
                "name": t.name,
                "type": t.table_type.value if t.table_type else "UNKNOWN",
                "owner": t.owner or "",
                "comment": t.comment or "",
            }
            for t in w.tables.list(catalog_name=catalog, schema_name=schema)
            if t.name
        ]
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{catalog}/{schema}/{table}")
async def get_table_detail(catalog: str, schema: str, table: str):
    try:
        w = _client()
        t = w.tables.get(full_name=f"{catalog}.{schema}.{table}")
        columns = []
        if t.columns:
            columns = [
                {
                    "name": c.name,
                    "type": c.type_text or str(c.type_name),
                    "nullable": c.nullable,
                    "comment": c.comment or "",
                }
                for c in t.columns
            ]
        return {
            "name": t.name,
            "type": t.table_type.value if t.table_type else "",
            "format": t.data_source_format.value if t.data_source_format else "",
            "owner": t.owner or "",
            "comment": t.comment or "",
            "columns": columns,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
