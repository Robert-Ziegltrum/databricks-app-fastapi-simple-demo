"""NYC Taxi analytics endpoints using samples.nyctaxi."""
from fastapi import APIRouter, Query
from utils.sql_client import run_query

router = APIRouter(prefix="/api/v1/taxi", tags=["taxi"])


def _where(fare_min: float, fare_max: float, dist_min: float, dist_max: float) -> str:
    return (f"WHERE fare_amount BETWEEN {fare_min} AND {fare_max}"
            f"  AND trip_distance BETWEEN {dist_min} AND {dist_max}"
            f"  AND trip_distance > 0 AND fare_amount > 0")


@router.get("/kpis")
async def get_kpis(
    fare_min: float = Query(0),
    fare_max: float = Query(100),
    dist_min: float = Query(0),
    dist_max: float = Query(20),
):
    w = _where(fare_min, fare_max, dist_min, dist_max)
    rows = run_query(f"""
        SELECT
            COUNT(*)                              AS total_trips,
            ROUND(AVG(fare_amount), 2)            AS avg_fare,
            ROUND(AVG(trip_distance), 2)          AS avg_distance,
            ROUND(AVG(fare_amount / NULLIF(trip_distance, 0)), 2) AS avg_fare_per_mile
        FROM samples.nyctaxi.trips {w}
    """)
    return rows[0] if rows else {}


@router.get("/distributions")
async def get_distributions(
    fare_min: float = Query(0),
    fare_max: float = Query(100),
    dist_min: float = Query(0),
    dist_max: float = Query(20),
    sample:   int   = Query(10000, le=100000),
):
    w = _where(fare_min, fare_max, dist_min, dist_max)
    return run_query(
        f"SELECT fare_amount, trip_distance FROM samples.nyctaxi.trips {w} LIMIT {sample}"
    )


@router.get("/hourly")
async def get_hourly(
    fare_min: float = Query(0),
    fare_max: float = Query(100),
    dist_min: float = Query(0),
    dist_max: float = Query(20),
):
    w = _where(fare_min, fare_max, dist_min, dist_max)
    return run_query(f"""
        SELECT
            HOUR(tpep_pickup_datetime)       AS hour_of_day,
            COUNT(*)                         AS trips,
            ROUND(AVG(fare_amount), 2)       AS avg_fare
        FROM samples.nyctaxi.trips {w}
        GROUP BY 1 ORDER BY 1
    """)


@router.get("/scatter")
async def get_scatter(
    fare_min: float = Query(0),
    fare_max: float = Query(100),
    dist_min: float = Query(0),
    dist_max: float = Query(20),
    sample:   int   = Query(2000, le=5000),
):
    w = _where(fare_min, fare_max, dist_min, dist_max)
    return run_query(
        f"SELECT fare_amount, trip_distance FROM samples.nyctaxi.trips {w} ORDER BY RAND() LIMIT {sample}"
    )
