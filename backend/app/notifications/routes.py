from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.notifications.models import UserNotificationPreference
from app.security.dependencies import get_current_user
from app.users.models import User


router = APIRouter(
    prefix="/api/v1/notification-preferences",
    tags=["notification-preferences"],
)


class NotificationPreferencesPayload(BaseModel):
    highlights_enabled: bool = False
    sentiment_enabled: bool = False
    approvals_enabled: bool = False


def _public_preferences(
    preferences: UserNotificationPreference | None,
) -> dict:
    if preferences is None:
        return {
            "highlights_enabled": False,
            "sentiment_enabled": False,
            "approvals_enabled": False,
            "updated_at": None,
        }

    return {
        "highlights_enabled": preferences.highlights_enabled,
        "sentiment_enabled": preferences.sentiment_enabled,
        "approvals_enabled": preferences.approvals_enabled,
        "updated_at": (
            preferences.updated_at.isoformat()
            if preferences.updated_at is not None
            else None
        ),
    }


@router.get("")
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = (
        db.query(UserNotificationPreference)
        .filter(UserNotificationPreference.user_id == current_user.id)
        .first()
    )

    return _public_preferences(preferences)


@router.put("")
def update_notification_preferences(
    payload: NotificationPreferencesPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = (
        db.query(UserNotificationPreference)
        .filter(UserNotificationPreference.user_id == current_user.id)
        .first()
    )

    now = datetime.now(timezone.utc)

    if preferences is None:
        preferences = UserNotificationPreference(
            user_id=current_user.id,
            highlights_enabled=payload.highlights_enabled,
            sentiment_enabled=payload.sentiment_enabled,
            approvals_enabled=payload.approvals_enabled,
            updated_at=now,
        )
        db.add(preferences)
    else:
        preferences.highlights_enabled = payload.highlights_enabled
        preferences.sentiment_enabled = payload.sentiment_enabled
        preferences.approvals_enabled = payload.approvals_enabled
        preferences.updated_at = now

    db.commit()
    db.refresh(preferences)

    return _public_preferences(preferences)