"""ProofChain Backend — FastAPI entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .api import api_router
from .services.workspace_service import workspace_store
from .agents.orchestrator import orchestrator
from .config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("proofchain")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup: seed demo data and run initial commitment intelligence pipeline."""
    logger.info("Initializing ProofChain...")
    try:
        ws = workspace_store.load_demo_data("demo-workspace")
        logger.info(f"Demo workspace initialized with {len(ws.documents)} documents.")
        # Trigger baseline analysis run
        run = orchestrator.run_pipeline("demo-workspace")
        logger.info(f"Baseline analysis complete. Status: {run.status.value}")
    except Exception as e:
        logger.warning(f"Startup initialization notice: {e}")
    yield
    logger.info("ProofChain shutting down.")


settings = get_settings()

app = FastAPI(
    title="ProofChain API",
    description="Evidence-Grounded Autonomous Professional Commitment Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router)


@app.get("/")
def root():
    """ProofChain root status."""
    return {
        "name": "ProofChain",
        "tagline": "Know what you promised. Prove you can deliver it.",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


@app.get("/health")
def healthcheck():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workspaces": len(workspace_store.list_workspaces()),
    }
