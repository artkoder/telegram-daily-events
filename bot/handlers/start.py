from aiogram import Router, types
from aiogram.filters import Command

from bot.services.admin import register_first_admin
from db.models import get_session, init_db

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    init_db()
    with get_session() as session:
        reply = register_first_admin(session, message.from_user.id)
        await message.answer(reply)
