import math
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


async def paginate(db: AsyncSession, query: Select, page: int = 1, page_size: int = 20) -> dict:
    """Generic pagination helper for SQLAlchemy queries."""
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0

    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    data = list(result.scalars().all())

    return {
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
