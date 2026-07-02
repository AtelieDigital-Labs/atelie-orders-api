from sqlalchemy.ext.asyncio import AsyncSession
from app.models.outbox import LogOutbox
from sqlalchemy import select


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_log(self):
        query = select(LogOutbox).where(LogOutbox.processed==False).order_by(LogOutbox.created_at).limit(50)
        result = await self.session.execute(query)
        logs = result.scalars(result).all()

        return logs