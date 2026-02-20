"""
Databricks Demo App — FastAPI backend.
Serves the REST API under /api/v1/* and the static frontend from /static.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import identity, sales, taxi, sql_explorer, catalog

app = FastAPI(
    title="Databricks Demo App",
    description="Interactive Databricks demo: identity, analytics, SQL explorer, and catalog browser.",
    docs_url="/docs",
    redoc_url="/redoc",
    version="1.0.0",
)

# ── API routers ───────────────────────────────────────────────────────────────
app.include_router(identity.router)
app.include_router(sales.router)
app.include_router(taxi.router)
app.include_router(sql_explorer.router)
app.include_router(catalog.router)

# ── Static frontend ───────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Catch-all: serve index.html for client-side routing."""
    index = "static/index.html"
    if os.path.exists(f"static/{full_path}"):
        return FileResponse(f"static/{full_path}")
    return FileResponse(index)