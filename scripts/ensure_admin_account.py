#!/usr/bin/env python3
"""Create or promote a production admin guardian account from environment values."""
from __future__ import annotations

import asyncio
import os
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import encrypt_pii, hash_email, hash_password
from app.models import Guardian, UserRole


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


async def ensure_admin() -> int:
    email = _required_env("DEV_ADMIN_EMAIL").lower()
    password = os.getenv("DEV_ADMIN_PASSWORD", "")
    display_name = os.getenv("DEV_ADMIN_DISPLAY_NAME", "EduBoost Admin").strip() or "EduBoost Admin"
    reset_password = os.getenv("RESET_DEV_ADMIN_PASSWORD", "false").strip().lower() in {"1", "true", "yes"}

    if password and len(password) < 12:
        raise RuntimeError("DEV_ADMIN_PASSWORD must be at least 12 characters when provided")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Guardian).where(Guardian.email_hash == hash_email(email)))
        guardian = result.scalar_one_or_none()

        if guardian is None:
            if not password:
                raise RuntimeError("DEV_ADMIN_PASSWORD is required when creating a new admin account")
            guardian = Guardian(
                email_hash=hash_email(email),
                email_encrypted=encrypt_pii(email),
                display_name=display_name,
                role=UserRole.ADMIN,
                password_hash=hash_password(password),
                is_active=True,
            )
            db.add(guardian)
            action = "created"
        else:
            guardian.display_name = display_name
            guardian.role = UserRole.ADMIN
            guardian.is_active = True
            if reset_password:
                guardian.password_hash = hash_password(password)
            action = "promoted"

        await db.commit()
        await db.refresh(guardian)
        print(f"Admin account {action}: {email} ({guardian.id})")
    return 0


def main() -> int:
    try:
        return asyncio.run(ensure_admin())
    except Exception as exc:
        print(f"Failed to ensure admin account: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
