from telegram import Bot
from config import PRODUCER_GROUP_ID


class MessagingService:

    def __init__(self, bot):
        self.bot = bot

    async def send_to_user(
        self,
        chat_id: int,
        text: str,
        reply_markup=None,
        parse_mode: str | None = None,
    ):
        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )

    async def send_to_group(
        self,
        text: str,
        reply_markup=None,
        parse_mode: str | None = None,
    ):
        await self.bot.send_message(
            chat_id=PRODUCER_GROUP_ID,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )

