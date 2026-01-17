"""Main FastAPI application entry point (Minimal for Troubleshooting)."""

import sys
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Force add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("🚀 Starting MINIMAL Focus Mate Backend...")
    yield
    logger.info("🛑 Stopping MINIMAL Focus Mate Backend...")

app = FastAPI(
    title="Minimal Troubleshooting App",
    lifespan=lifespan,
)

@app.get("/")
async def root():
    return {"message": "Minimal App Running", "sys_path": sys.path}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
