from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ChatMessage import ChatMessage
from app.core.logger.app_logger import log

ic.configureOutput(includeContext=True)


async def save_chat_message(db_session: AsyncSession, chat_message: ChatMessage) -> None:
    log.info("Starting to save chat message")

    db_session.add(chat_message)
    await db_session.commit()

    log.info("Chat message saved successfully")
