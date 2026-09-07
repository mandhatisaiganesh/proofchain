"""ProofChain API Routers."""

from fastapi import APIRouter

from .workspace import router as workspace_router
from .documents import router as documents_router
from .analysis import router as analysis_router
from .commitments import router as commitments_router
from .graph import router as graph_router
from .conflicts import router as conflicts_router
from .risks import router as risks_router
from .actions import router as actions_router
from .scenarios import router as scenarios_router

api_router = APIRouter()
api_router.include_router(workspace_router)
api_router.include_router(documents_router)
api_router.include_router(analysis_router)
api_router.include_router(commitments_router)
api_router.include_router(graph_router)
api_router.include_router(conflicts_router)
api_router.include_router(risks_router)
api_router.include_router(actions_router)
api_router.include_router(scenarios_router)

__all__ = ["api_router"]
