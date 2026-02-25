"""FastAPI application entry point for langchain-poc."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat, kb, webhooks, workflows
from app.odoo.auth import test_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run startup tasks, then yield."""
    logger.info("Starting langchain-poc application")
    ok = test_connection()
    if ok:
        logger.info("odoo_connection", status="ok")
    else:
        logger.warning("odoo_connection", status="failed — check .env settings")
    yield
    logger.info("Shutting down langchain-poc application")


app = FastAPI(
    title="langchain-poc",
    description="LangChain multi-agent application integrated with Odoo 16 CRM",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins for POC
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
app.include_router(kb.router, prefix="/kb", tags=["knowledge_base"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Serve static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")
