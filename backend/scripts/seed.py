"""
Database seeder for ElderOS — creates demo data for development and testing.

Usage:
    python scripts/seed.py

Idempotent: checks for existing data before inserting.
"""

import asyncio
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select

from src.config import settings  # noqa: E402
from src.core.security import hash_password  # noqa: E402
from src.database import Base, async_session_factory  # noqa: E402
from src.models import (  # noqa: E402
    CallBellEvent,
    ConfidenceThreshold,
    EscalationRule,
    Event,
    Incident,
    Resident,
    RetentionPolicy,
    Room,
    Sensor,
    SystemMetrics,
    Unit,
    User,
)

# Re-create the engine with the same settings for standalone script usage
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(settings.database_url, echo=False)
session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

NOW = datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Margaret", "Dorothy", "Helen", "Ruth", "Virginia", "Elizabeth",
    "Frances", "Evelyn", "Alice", "Jean", "Robert", "James", "John",
    "William", "Charles", "George", "Edward", "Frank", "Harold", "Henry",
    "Betty", "Shirley", "Barbara", "Patricia", "Doris", "Nancy",
    "Catherine", "Eleanor", "Mildred", "Gladys", "Thomas", "Arthur",
    "Walter", "Albert", "Herbert", "Raymond", "Kenneth", "Donald",
    "Eugene", "Howard", "Josephine", "Rose", "Lillian", "Grace",
    "Marie", "Lucille", "Irene", "Theresa",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor",
    "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson",
    "White", "Harris", "Clark", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres",
    "Nguyen", "Hill", "Adams", "Baker", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell",
    "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris",
]

EVENT_TYPES = ["fall", "bed-exit", "inactivity", "unsafe-transfer"]
EVENT_WEIGHTS = [0.2, 0.4, 0.25, 0.15]
EVENT_STATUSES = ["active", "acknowledged", "resolved", "dismissed", "escalated"]
EVENT_STATUS_WEIGHTS = [0.05, 0.1, 0.6, 0.15, 0.1]
CONFIDENCE_LEVELS = ["high", "medium", "low"]
SENSOR_TYPES = ["ai-vision", "ai-sensor"]
SENSOR_SOURCES = ["ai-vision", "ai-sensor", "fused"]
CALL_ORIGINS = ["bedside", "bathroom", "hallway", "pendant"]
CALL_PRIORITIES = ["emergency", "urgent", "normal"]
CALL_PRIORITY_WEIGHTS = [0.05, 0.2, 0.75]
CALL_VENDORS = ["jeron", "rauland", "hill-rom"]
SHIFTS = ["day", "evening", "night"]

PRE_EVENT_SUMMARIES = [
    "Resident was in bed, restless movement detected.",
    "Resident sitting in chair near bedside.",
    "Resident ambulating slowly in room.",
    "Resident appeared to be reaching for item on nightstand.",
    "Resident was transferring from wheelchair to bed.",
    "Resident standing at bedside, swaying detected.",
    "Resident rolling in bed, attempting to sit up.",
    "No significant movement for extended period.",
]

POST_EVENT_STATES = [
    "Resident found on floor, alert and oriented.",
    "Resident returned to bed by staff, no injury noted.",
    "Resident assisted back to chair, vitals stable.",
    "Resident on floor near bed, minor bruise noted.",
    "Staff arrived, resident still in bed, no fall confirmed.",
    "Resident assisted, incident documented.",
    "Resident stable, family notified.",
    "Resident repositioned, monitoring continues.",
]


def uid() -> str:
    return str(uuid.uuid4())


def rand_dt(days_back: int = 30) -> datetime:
    """Random datetime within the last N days."""
    offset = random.randint(0, days_back * 24 * 3600)
    return NOW - timedelta(seconds=offset)


def initials(name: str) -> str:
    parts = name.split()
    return "".join(p[0].upper() for p in parts[:2])


def pick_shift(dt: datetime) -> str:
    hour = dt.hour
    if 7 <= hour < 15:
        return "day"
    elif 15 <= hour < 23:
        return "evening"
    return "night"


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------


async def seed_users(session: AsyncSession) -> list[User]:
    existing = (await session.execute(select(User))).scalars().all()
    if existing:
        print(f"  Users: {len(existing)} already exist, skipping.")
        return list(existing)

    password_hash = hash_password("demo123")

    users_data = [
        {"name": "Admin User", "email": "admin@elderos.local", "role": "admin", "unit": "All"},
        {"name": "Sarah Chen", "email": "supervisor@elderos.local", "role": "supervisor", "unit": "All"},
        {"name": "Maria Lopez", "email": "nurse1@elderos.local", "role": "nurse", "unit": "East Wing"},
        {"name": "James Park", "email": "nurse2@elderos.local", "role": "nurse", "unit": "West Wing"},
        {"name": "Aisha Patel", "email": "psw1@elderos.local", "role": "psw", "unit": "East Wing"},
    ]

    users = []
    for u in users_data:
        user = User(
            id=uid(),
            name=u["name"],
            email=u["email"],
            password_hash=password_hash,
            role=u["role"],
            unit=u["unit"],
            avatar_initials=initials(u["name"]),
            is_active=True,
        )
        session.add(user)
        users.append(user)

    await session.flush()
    print(f"  Users: created {len(users)}")
    return users


async def seed_units(session: AsyncSession) -> list[Unit]:
    existing = (await session.execute(select(Unit))).scalars().all()
    if existing:
        print(f"  Units: {len(existing)} already exist, skipping.")
        return list(existing)

    units_data = [
        {"name": "East Wing", "floor": 2},
        {"name": "West Wing", "floor": 3},
    ]

    units = []
    for u in units_data:
        unit = Unit(id=uid(), name=u["name"], floor=u["floor"])
        session.add(unit)
        units.append(unit)

    await session.flush()
    print(f"  Units: created {len(units)}")
    return units


async def seed_rooms(session: AsyncSession, units: list[Unit]) -> list[Room]:
    existing = (await session.execute(select(Room))).scalars().all()
    if existing:
        print(f"  Rooms: {len(existing)} already exist, skipping.")
        return list(existing)

    room_types = ["single", "semi-private"]
    sensor_types_list = ["ai-vision", "ai-sensor", "hybrid"]

    rooms = []
    for unit in units:
        start = 201 if unit.floor == 2 else 301
        for i in range(25):
            room_num = str(start + i)
            sensor_type = random.choice(sensor_types_list)
            room = Room(
                id=uid(),
                number=room_num,
                unit_id=unit.id,
                unit_name=unit.name,
                floor=unit.floor,
                room_type=random.choice(room_types),
                sensor_type=sensor_type,
                status="clear",
                status_color="green",
                has_exclusion_zone=random.random() < 0.2,
            )
            session.add(room)
            rooms.append(room)

    await session.flush()
    print(f"  Rooms: created {len(rooms)}")
    return rooms


async def seed_residents(session: AsyncSession, rooms: list[Room]) -> list[Resident]:
    existing = (await session.execute(select(Resident))).scalars().all()
    if existing:
        print(f"  Residents: {len(existing)} already exist, skipping.")
        return list(existing)

    # Distribute 48 residents across rooms — some empty, some doubles
    available_rooms = list(rooms)
    random.shuffle(available_rooms)

    residents = []
    used_names = set()
    room_idx = 0

    for i in range(48):
        # Generate unique name
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full = f"{first} {last}"
            if full not in used_names:
                used_names.add(full)
                break

        room = available_rooms[room_idx % len(available_rooms)]
        # Advance room index — first 48 rooms get at least one, some get two
        if i < len(available_rooms):
            room_idx += 1
        else:
            # Second pass — doubles
            room_idx += 1

        # Determine bed zone for semi-private rooms
        bed_zone = None
        if room.room_type == "semi-private":
            # Check if room already has a resident
            existing_in_room = [r for r in residents if r.room_id == room.id]
            bed_zone = "A" if not existing_in_room else "B"

        risk_score = random.randint(10, 95)
        fall_count = random.randint(0, 4)
        admitted_days_ago = random.randint(14, 365)

        resident = Resident(
            id=uid(),
            name=full,
            room_id=room.id,
            room_number=room.number,
            unit=room.unit_name,
            bed_zone=bed_zone,
            age=random.randint(65, 98),
            risk_score=risk_score,
            risk_trend=random.choice(["stable", "increasing", "decreasing"]),
            fall_count_30d=min(fall_count, 2),
            fall_count_total=fall_count,
            last_fall_date=rand_dt(60) if fall_count > 0 else None,
            last_event_date=rand_dt(14) if random.random() > 0.3 else None,
            admitted_at=NOW - timedelta(days=admitted_days_ago),
            observe_only=random.random() < 0.1,
        )
        session.add(resident)
        residents.append(resident)

    await session.flush()
    print(f"  Residents: created {len(residents)}")
    return residents


async def seed_sensors(session: AsyncSession, rooms: list[Room]) -> list[Sensor]:
    existing = (await session.execute(select(Sensor))).scalars().all()
    if existing:
        print(f"  Sensors: {len(existing)} already exist, skipping.")
        return list(existing)

    sensors = []
    for room in rooms:
        # Determine how many sensors based on room sensor_type
        if room.sensor_type == "hybrid":
            types_to_add = ["ai-vision", "ai-sensor"]
        elif room.sensor_type == "ai-vision":
            types_to_add = ["ai-vision"]
        else:
            types_to_add = ["ai-sensor"]

        for s_type in types_to_add:
            sensor = Sensor(
                id=uid(),
                room_id=room.id,
                room_number=room.number,
                type=s_type,
                status=random.choices(["online", "offline"], weights=[0.95, 0.05])[0],
                last_heartbeat=NOW - timedelta(seconds=random.randint(0, 300)),
                inference_latency_ms=random.randint(40, 200),
                baseline_latency_ms=80,
                uptime=round(random.uniform(95.0, 99.99), 2),
                firmware_version=random.choice(["v1.0.0", "v1.1.0", "v1.2.0"]),
            )
            session.add(sensor)
            sensors.append(sensor)

    await session.flush()
    print(f"  Sensors: created {len(sensors)}")
    return sensors


async def seed_events(
    session: AsyncSession,
    rooms: list[Room],
    residents: list[Resident],
    users: list[User],
) -> list[Event]:
    existing = (await session.execute(select(Event))).scalars().all()
    if existing:
        print(f"  Events: {len(existing)} already exist, skipping.")
        return list(existing)

    staff_users = [u for u in users if u.role in ("nurse", "psw", "supervisor")]

    events = []
    for _ in range(510):
        room = random.choice(rooms)
        # Find residents in this room
        room_residents = [r for r in residents if r.room_id == room.id]
        resident = random.choice(room_residents) if room_residents else None

        event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS)[0]
        status = random.choices(EVENT_STATUSES, weights=EVENT_STATUS_WEIGHTS)[0]
        detected_at = rand_dt(30)

        conf_score = random.randint(30, 99)
        if conf_score >= 85:
            confidence = "high"
        elif conf_score >= 60:
            confidence = "medium"
        else:
            confidence = "low"

        severity = "critical" if event_type == "fall" else random.choice(["high", "medium", "low"])

        ack_by = None
        ack_at = None
        resolve_by = None
        resolve_at = None
        escalation_level = 0

        if status in ("acknowledged", "resolved", "dismissed"):
            ack_seconds = random.randint(15, 600)
            ack_at = detected_at + timedelta(seconds=ack_seconds)
            ack_by = random.choice(staff_users).id

        if status == "resolved":
            resolve_seconds = random.randint(60, 1800)
            resolve_at = detected_at + timedelta(seconds=resolve_seconds)
            resolve_by = random.choice(staff_users).id

        if status == "escalated":
            escalation_level = random.choice([1, 2, 3])

        is_repeat = False
        if resident and event_type == "fall" and resident.fall_count_30d > 1:
            is_repeat = True

        event = Event(
            id=uid(),
            room_id=room.id,
            room_number=room.number,
            resident_id=resident.id if resident else None,
            resident_name=resident.name if resident else None,
            event_type=event_type,
            severity=severity,
            confidence=confidence,
            confidence_score=conf_score,
            status=status,
            detected_at=detected_at,
            acknowledged_at=ack_at,
            resolved_at=resolve_at,
            acknowledged_by=ack_by,
            resolved_by=resolve_by,
            escalation_level=escalation_level,
            pre_event_summary=random.choice(PRE_EVENT_SUMMARIES),
            post_event_state=random.choice(POST_EVENT_STATES) if status == "resolved" else None,
            is_repeat_fall=is_repeat,
            unit=room.unit_name,
            sensor_source=random.choice(SENSOR_SOURCES),
            bed_zone=resident.bed_zone if resident else None,
        )
        session.add(event)
        events.append(event)

    await session.flush()
    print(f"  Events: created {len(events)}")
    return events


async def seed_call_bells(
    session: AsyncSession,
    rooms: list[Room],
    residents: list[Resident],
    users: list[User],
) -> None:
    existing = (await session.execute(select(CallBellEvent))).scalars().all()
    if existing:
        print(f"  Call Bells: {len(existing)} already exist, skipping.")
        return

    staff_users = [u for u in users if u.role in ("nurse", "psw", "supervisor")]

    for _ in range(900):
        room = random.choice(rooms)
        room_residents = [r for r in residents if r.room_id == room.id]
        resident = random.choice(room_residents) if room_residents else None

        pressed_at = rand_dt(30)
        priority = random.choices(CALL_PRIORITIES, weights=CALL_PRIORITY_WEIGHTS)[0]

        # Most calls get responded to
        responded = random.random() < 0.9
        responded_at = None
        closed_at = None
        response_time = None
        responder = None
        responder_name = None
        status = "active"

        if responded:
            response_time = random.randint(10, 480)
            responded_at = pressed_at + timedelta(seconds=response_time)
            responder_obj = random.choice(staff_users)
            responder = responder_obj.id
            responder_name = responder_obj.name
            if random.random() < 0.85:
                closed_at = responded_at + timedelta(seconds=random.randint(30, 600))
                status = "closed"
            else:
                status = "responded"

        call = CallBellEvent(
            id=uid(),
            room_id=room.id,
            room_number=room.number,
            resident_id=resident.id if resident else None,
            resident_name=resident.name if resident else None,
            unit=room.unit_name,
            floor=room.floor,
            origin=random.choice(CALL_ORIGINS),
            priority=priority,
            status=status,
            vendor=random.choice(CALL_VENDORS),
            pressed_at=pressed_at,
            responded_at=responded_at,
            closed_at=closed_at,
            response_time_seconds=response_time,
            responded_by=responder,
            responded_by_name=responder_name,
            shift=pick_shift(pressed_at),
        )
        session.add(call)

    await session.flush()
    print("  Call Bells: created 900")


async def seed_incidents(session: AsyncSession, events: list[Event]) -> list[Incident]:
    existing = (await session.execute(select(Incident))).scalars().all()
    if existing:
        print(f"  Incidents: {len(existing)} already exist, skipping.")
        return list(existing)

    resolved_events = [e for e in events if e.status == "resolved"]
    incident_events = resolved_events[:200] if len(resolved_events) >= 200 else resolved_events

    incidents = []
    for ev in incident_events:
        ack_seconds = None
        resolve_seconds = None
        if ev.acknowledged_at and ev.detected_at:
            ack_seconds = int((ev.acknowledged_at - ev.detected_at).total_seconds())
        if ev.resolved_at and ev.detected_at:
            resolve_seconds = int((ev.resolved_at - ev.detected_at).total_seconds())

        incident = Incident(
            id=uid(),
            event_id=ev.id,
            room_number=ev.room_number,
            resident_name=ev.resident_name,
            resident_id=ev.resident_id,
            event_type=ev.event_type,
            confidence=ev.confidence,
            confidence_score=ev.confidence_score,
            status=ev.status,
            ntp_timestamp=ev.detected_at.isoformat() if ev.detected_at else None,
            detected_at=ev.detected_at,
            acknowledged_at=ev.acknowledged_at,
            resolved_at=ev.resolved_at,
            ack_response_seconds=ack_seconds,
            resolve_response_seconds=resolve_seconds,
            acknowledged_by=ev.acknowledged_by,
            resolved_by=ev.resolved_by,
            pre_event_summary=ev.pre_event_summary,
            post_event_state=ev.post_event_state,
            is_repeat_fall=ev.is_repeat_fall,
            notes="",
            unit=ev.unit,
            sensor_source=ev.sensor_source,
            bed_zone=ev.bed_zone,
        )
        session.add(incident)
        incidents.append(incident)

    await session.flush()
    print(f"  Incidents: created {len(incidents)}")
    return incidents


async def seed_system_metrics(session: AsyncSession) -> None:
    existing = (await session.execute(select(SystemMetrics))).scalars().all()
    if existing:
        print(f"  System Metrics: {len(existing)} already exist, skipping.")
        return

    for day_offset in range(30):
        recorded_at = NOW - timedelta(days=day_offset)
        metric = SystemMetrics(
            id=uid(),
            cpu_usage=round(random.uniform(15.0, 65.0), 1),
            memory_usage=round(random.uniform(30.0, 75.0), 1),
            disk_usage_percent=round(random.uniform(20.0, 60.0), 1),
            disk_used_gb=round(random.uniform(40.0, 120.0), 1),
            disk_total_gb=200.0,
            retention_days=7,
            auto_purge_threshold_percent=90,
            ntp_drift_ms=random.randint(0, 15),
            ntp_sync_status="synced" if random.random() > 0.05 else "drifting",
            last_self_test_at=recorded_at - timedelta(hours=random.randint(0, 6)),
            self_test_passed=random.random() > 0.02,
            edge_device_uptime=f"{random.randint(1, 90)}d {random.randint(0, 23)}h {random.randint(0, 59)}m",
            recorded_at=recorded_at,
        )
        session.add(metric)

    await session.flush()
    print("  System Metrics: created 30")


async def seed_escalation_rules(session: AsyncSession) -> None:
    existing = (await session.execute(select(EscalationRule))).scalars().all()
    if existing:
        print(f"  Escalation Rules: {len(existing)} already exist, skipping.")
        return

    rules = [
        {"delay_minutes": 3, "action": "sms", "target": "on-duty nurse"},
        {"delay_minutes": 5, "action": "page", "target": "charge nurse"},
        {"delay_minutes": 10, "action": "call", "target": "supervisor on-call"},
    ]

    for rule in rules:
        session.add(EscalationRule(
            id=uid(),
            delay_minutes=rule["delay_minutes"],
            action=rule["action"],
            target=rule["target"],
            enabled=True,
        ))

    await session.flush()
    print("  Escalation Rules: created 3")


async def seed_confidence_thresholds(session: AsyncSession) -> None:
    existing = (await session.execute(select(ConfidenceThreshold))).scalars().all()
    if existing:
        print("  Confidence Thresholds: already exist, skipping.")
        return

    session.add(ConfidenceThreshold(
        id=1,
        high_min=85,
        medium_min=60,
        low_min=30,
    ))
    await session.flush()
    print("  Confidence Thresholds: created")


async def seed_retention_policy(session: AsyncSession) -> None:
    existing = (await session.execute(select(RetentionPolicy))).scalars().all()
    if existing:
        print("  Retention Policy: already exists, skipping.")
        return

    session.add(RetentionPolicy(
        id=1,
        clip_retention_days=7,
        metadata_retention_days=90,
        auto_purge_enabled=True,
        purge_threshold_percent=90,
    ))
    await session.flush()
    print("  Retention Policy: created")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    print("ElderOS Database Seeder")
    print(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'local'}")
    print("-" * 50)

    async with session_factory() as session:
        async with session.begin():
            users = await seed_users(session)
            units = await seed_units(session)
            rooms = await seed_rooms(session, units)
            residents = await seed_residents(session, rooms)
            sensors = await seed_sensors(session, rooms)
            events = await seed_events(session, rooms, residents, users)
            await seed_call_bells(session, rooms, residents, users)
            await seed_incidents(session, events)
            await seed_system_metrics(session)
            await seed_escalation_rules(session)
            await seed_confidence_thresholds(session)
            await seed_retention_policy(session)

    print("-" * 50)
    print("Seed complete.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
