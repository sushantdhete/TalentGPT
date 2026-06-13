"""
TalentGPT - AI Recruiter Intelligence Platform
FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 TalentGPT starting up...")
    await create_tables()
    logger.info("✅ Database tables initialized")
    yield
    logger.info("🛑 TalentGPT shutting down...")


app = FastAPI(
    title="TalentGPT API",
    description="AI Recruiter Intelligence Platform - Enterprise Grade Talent Matching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TalentGPT API",
        "version": "1.0.0"
    }
