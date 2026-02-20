"""Sales analytics endpoints using samples.tpch."""
from fastapi import APIRouter, Query
from utils.sql_client import run_query

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])


def _status_clause(status: str) -> str:
    if status == "ALL":
        return ""
    return f"AND o.o_orderstatus = '{status}'"


@router.get("/kpis")
async def get_kpis(
    year_from: int = Query(1994, ge=1992, le=1998),
    year_to:   int = Query(1997, ge=1992, le=1998),
    status:    str = Query("ALL"),
):
    sf = _status_clause(status)
    rows = run_query(f"""
        SELECT
            COUNT(DISTINCT o.o_orderkey)  AS total_orders,
            COUNT(DISTINCT o.o_custkey)   AS unique_customers,
            ROUND(SUM(o.o_totalprice), 0) AS total_revenue,
            ROUND(AVG(o.o_totalprice), 2) AS avg_order_value
        FROM samples.tpch.orders o
        WHERE YEAR(o.o_orderdate) BETWEEN {year_from} AND {year_to}
        {sf}
    """)
    return rows[0] if rows else {}


@router.get("/trend")
async def get_trend(
    year_from: int = Query(1994, ge=1992, le=1998),
    year_to:   int = Query(1997, ge=1992, le=1998),
    status:    str = Query("ALL"),
):
    sf = _status_clause(status)
    return run_query(f"""
        SELECT
            DATE_TRUNC('month', o.o_orderdate) AS month,
            ROUND(SUM(o.o_totalprice), 0)      AS revenue
        FROM samples.tpch.orders o
        WHERE YEAR(o.o_orderdate) BETWEEN {year_from} AND {year_to}
        {sf}
        GROUP BY 1 ORDER BY 1
    """)


@router.get("/by-region")
async def get_by_region(
    year_from: int = Query(1994, ge=1992, le=1998),
    year_to:   int = Query(1997, ge=1992, le=1998),
    status:    str = Query("ALL"),
):
    sf = _status_clause(status)
    return run_query(f"""
        SELECT
            r.r_name                           AS region,
            n.n_name                           AS nation,
            ROUND(SUM(o.o_totalprice), 0)      AS revenue
        FROM samples.tpch.orders o
        JOIN samples.tpch.customer c ON o.o_custkey   = c.c_custkey
        JOIN samples.tpch.nation   n ON c.c_nationkey = n.n_nationkey
        JOIN samples.tpch.region   r ON n.n_regionkey = r.r_regionkey
        WHERE YEAR(o.o_orderdate) BETWEEN {year_from} AND {year_to}
        {sf}
        GROUP BY 1, 2 ORDER BY 1, 3 DESC
    """)


@router.get("/top-customers")
async def get_top_customers(
    year_from: int = Query(1994, ge=1992, le=1998),
    year_to:   int = Query(1997, ge=1992, le=1998),
    status:    str = Query("ALL"),
    limit:     int = Query(10, ge=5, le=25),
):
    sf = _status_clause(status)
    return run_query(f"""
        SELECT
            c.c_name                            AS customer,
            c.c_mktsegment                      AS segment,
            COUNT(o.o_orderkey)                 AS orders,
            ROUND(SUM(o.o_totalprice), 0)       AS revenue,
            ROUND(AVG(o.o_totalprice), 2)       AS avg_order
        FROM samples.tpch.orders o
        JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
        WHERE YEAR(o.o_orderdate) BETWEEN {year_from} AND {year_to}
        {sf}
        GROUP BY 1, 2 ORDER BY 4 DESC LIMIT {limit}
    """)
