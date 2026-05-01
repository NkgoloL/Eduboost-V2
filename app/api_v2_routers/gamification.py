"""Gamification routes for EduBoost V2."""

from fastapi import APIRouter

from app.services.gamification_service_v2 import GamificationServiceV2

router = APIRouter(prefix="/api/v2/gamification", tags=["V2 Gamification"])


@router.get("/profile/{learner_id}")
async def get_profile(learner_id: str):
    return await GamificationServiceV2().get_profile(learner_id)


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    return await GamificationServiceV2().leaderboard(limit=limit)
