from fastapi import APIRouter

from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.charts import router as charts_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.compatibility import router as compatibility_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.metrics import router as metrics_router
from backend.app.api.v1.profiles import router as profiles_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.transits import router as transits_router

api_v1_router = APIRouter()

# Mount health probes directly or under v1
api_v1_router.include_router(health_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(charts_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(compatibility_router)
api_v1_router.include_router(transits_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(metrics_router)
