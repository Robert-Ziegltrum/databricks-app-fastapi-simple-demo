# 🧱 Databricks Demo App — FastAPI

A realistic, interactive Databricks App built with **FastAPI** (backend) and **vanilla JS + Plotly** (frontend), deployed directly from Git — zero manual setup.

## Architecture

Unlike Streamlit and Dash, FastAPI is a pure API framework. This app combines:
- **FastAPI backend** — REST API under `/api/v1/*`, serving data from Databricks SQL + SDK
- **Vanilla JS SPA** — single `static/index.html` with Plotly CDN, fetching data from the API
- FastAPI serves the static frontend via `StaticFiles` — one process, one port, one deployment

## Views

| Page | API Endpoints | Data Source |
|---|---|---|
| 🏠 Home | — | — |
| 👤 Identity & Access | `GET /api/v1/identity/me` | HTTP headers + SDK |
| 💰 Sales Analytics | `GET /api/v1/sales/kpis`, `/trend`, `/by-region`, `/top-customers` | `samples.tpch` |
| 🚕 NYC Taxi | `GET /api/v1/taxi/kpis`, `/distributions`, `/hourly`, `/scatter` | `samples.nyctaxi` |
| 🔍 SQL Explorer | `POST /api/v1/sql/run` | `samples.*` |
| 📂 Catalog Browser | `GET /api/v1/catalog/catalogs`, `/schemas`, `/tables`, `/detail` | Unity Catalog API |

## Prerequisites

- Databricks workspace with Unity Catalog enabled
- Serverless SQL Warehouse or standard SQL Warehouse
- Foundation Model APIs enabled (default in most regions)

## Deploy from Git

1. Go to **Compute → Apps → Create App → Custom App**
2. Choose **Deploy from Git**, enter this repository URL
3. Click **Deploy**

The app auto-discovers a SQL Warehouse. Optionally set `DATABRICKS_WAREHOUSE_ID` in `app.yaml`.

## Run Locally

```bash
pip install -r requirements.txt
export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
databricks auth login   # or set DATABRICKS_TOKEN
uvicorn app:app --reload --port 8080
```

Open http://localhost:8080. API docs available at http://localhost:8080/docs.

## Structure

```
.
├── app.py                   # FastAPI entry point, mounts routers + static files
├── app.yaml                 # Databricks Apps config
├── requirements.txt
├── .gitignore
├── routers/
│   ├── identity.py          # GET /api/v1/identity/me
│   ├── sales.py             # GET /api/v1/sales/*
│   ├── taxi.py              # GET /api/v1/taxi/*
│   ├── sql_explorer.py      # POST /api/v1/sql/run
│   ├── catalog.py           # GET /api/v1/catalog/*
│   └── ai.py                # POST /api/v1/ai/chat
├── utils/
│   └── sql_client.py        # Shared SQL connection + warehouse auto-discovery
└── static/
    └── index.html           # Full SPA: all 6 views in vanilla JS + Plotly CDN
```

## API Docs

FastAPI auto-generates interactive API documentation at `/docs` (Swagger UI) and `/redoc`.
