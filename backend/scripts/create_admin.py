"""
CLI script to create an admin user in the ElderOS database.

Usage:
    python scripts/create_admin.py --email admin@elderos.local --password securepass --name "Admin User"

Options:
    --email       Email address for the admin user (required)
    --password    Password for the admin user (required)
    --name        Display name for the admin user (required)
    --unit        Unit assignment (default: "All")
"""

import argparse
import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings  # noqa: E402
from src.core.security import hash_password  # noqa: E402
from src.models import User  # noqa: E402

engine = create_async_engine(settings.database_url, echo=False)
session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def initials(name: str) -> str:
    """Extract up to 2-character initials from a full name."""
    parts = name.strip().split()
    return "".join(p[0].upper() for p in parts[:2])


async def create_admin(email: str, password: str, name: str, unit: str) -> None:
    async with session_factory() as session:
        async with session.begin():
            # Check if user with this email already exists
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Error: User with email '{email}' already exists (id={existing.id}, role={existing.role}).")
                sys.exit(1)

            user = User(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                password_hash=hash_password(password),
                role="admin",
                unit=unit,
                avatar_initials=initials(name),
                is_active=True,
            )
            session.add(user)

    print(f"Admin user created successfully.")
    print(f"  ID:    {user.id}")
    print(f"  Name:  {name}")
    print(f"  Email: {email}")
    print(f"  Role:  admin")
    print(f"  Unit:  {unit}")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an admin user in the ElderOS database."
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Email address for the admin user",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password for the admin user",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Display name for the admin user",
    )
    parser.add_argument(
        "--unit",
        default="All",
        help="Unit assignment (default: All)",
    )

    args = parser.parse_args()

    if len(args.password) < 8:
        print("Error: Password must be at least 8 characters.")
        sys.exit(1)

    asyncio.run(create_admin(
        email=args.email,
        password=args.password,
        name=args.name,
        unit=args.unit,
    ))


if __name__ == "__main__":
    main()
