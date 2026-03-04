from fastapi import APIRouter

from src.api import (
    alerts,
    auth,
    call_bell,
    devices,
    edge,
    facility,
    incidents,
    reports,
    residents,
    review,
    rooms,
    settings,
    system,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(residents.router, prefix="/residents", tags=["residents"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(facility.router, prefix="/facility", tags=["facility"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(call_bell.router, prefix="/call-bell", tags=["call-bell"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(edge.router, prefix="/edge", tags=["edge"])
