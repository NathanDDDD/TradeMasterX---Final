import logging
from telegram import Bot
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class TelegramPublisher:
    def __init__(self, token: str, channel_id: str):
        self.bot = Bot(token=token)
        self.channel_id = channel_id

    async def send(self, message: str) -> bool:
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info(f"Message sent to {self.channel_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
