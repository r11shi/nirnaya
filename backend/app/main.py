"""Nirnaya Backend — Main FastAPI Application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.health import router as health_router
from app.api.fraud import router as fraud_router
from app.api.finance import router as finance_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("Starting Nirnaya backend...")
    
    # Create database tables
    await init_db()
    logger.info(f"Database initialized: {settings.DATABASE_URL}")
    logger.info(f"LLM provider: {settings.DEFAULT_LLM_PROVIDER}")
    
    yield
    
    logger.info("Nirnaya backend shutting down.")


app = FastAPI(
    title="Nirnaya",
    description="Personal Financial Risk & Decision Support System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(fraud_router)
app.include_router(finance_router)


@app.get("/")
async def root():
    return {
        "name": "Nirnaya",
        "description": "Personal Financial Risk & Decision Support System",
        "docs": "/docs",
    }
