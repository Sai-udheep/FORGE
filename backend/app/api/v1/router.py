from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.categories import router as categories_router
from app.api.v1.goals import router as goals_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.planner import router as planner_router
from app.api.v1.reminders import router as reminders_router
from app.api.v1.focus import router as focus_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.integrations import router as integrations_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(categories_router)
api_router.include_router(goals_router)
api_router.include_router(tasks_router)
api_router.include_router(planner_router)
api_router.include_router(reminders_router)
api_router.include_router(focus_router)
api_router.include_router(reviews_router)
api_router.include_router(analytics_router)
api_router.include_router(integrations_router)
