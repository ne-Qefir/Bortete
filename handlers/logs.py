from aiogram import Router, types, Bot, F
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters import ChatTypeFilter
from typing import Optional
import DB.database as db
import json
import os

router = Router()


class Logs_group:
    async def set_group(self, data):
        with open(
            os.path.dirname(__file__) + r"\logs.json", "w", encoding="utf-8"
        ) as file:
            json.dump(data, file, indent=2, ensure_ascii=False)


@router.message(ChatTypeFilter(chat_type=["group", "supergroup"]))
async def admins_comm(message: Message):
    if message.from_user.id not in (await db.get_admin()):
        return
    if message.text == "!logs":
        await Logs_group().set_group({"group_id": message.chat.id})
        await message.answer("Группа выбрана для отправки логов!")
