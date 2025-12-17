"""API v1 router - aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    achievements,
    auth,
    chat,
    community,
    matching,
    messaging,
    notifications,
    participants,
    proposals,
    ranking,
    room_reservations,
    rooms,
    settings,
    stats,
    timer,
    verification,
    websocket,
)

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
api_router.include_router(ranking.router)
api_router.include_router(room_reservations.router)
api_router.include_router(verification.router)
api_router.include_router(matching.router)
api_router.include_router(proposals.router)
api_router.include_router(chat.router)
api_router.include_router(notifications.router)
api_router.include_router(settings.router)
