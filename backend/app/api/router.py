"""Root API router configuring versioned endpoints."""

from fastapi import APIRouter
from app.api.v1 import (
    ai,
    audit,
    dashboard,
    health,
    investigations,
    pipeline,
    recovery,
    risk,
    simulation,
    transactions,
)

api_router = APIRouter()

# Version 1 Router Aggregation
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(health.router)
v1_router.include_router(simulation.router)
v1_router.include_router(transactions.router)
v1_router.include_router(risk.router)
v1_router.include_router(dashboard.router)
v1_router.include_router(pipeline.router)
v1_router.include_router(audit.router)
v1_router.include_router(investigations.router)
v1_router.include_router(ai.router)
v1_router.include_router(recovery.router)

# Mount /v1 router under root API router
api_router.include_router(v1_router)

