"""API v1 router - aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import achievements, auth, community, messaging, participants, rooms, stats, timer, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(rooms.router)
api_router.include_router(timer.router)
api_router.include_router(participants.router)
api_router.include_router(stats.router)
api_router.include_router(achievements.router)
api_router.include_router(community.router)
api_router.include_router(messaging.router)
api_router.include_router(websocket.router)
