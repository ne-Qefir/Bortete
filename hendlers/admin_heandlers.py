from aiogram import Router, types, Bot
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from typing import Optional
import sys
import os
import json

sys.path.append("./DB")
import database


router = Router()


class Get_text_state(StatesGroup):
    get_text = State()


class Get_text2_state(StatesGroup):
    get_text = State()


class Get_post_state(StatesGroup):
    get_post = State()


# Хэндлер на /admin
@router.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id not in (await database.get_admin()):
        return
    await message.answer(
        text="Это админ панель, выбери действие:",
        reply_markup=(await get_admin_menu()).as_markup(),
    )


class Audio_text:
    async def set_text(self, text):
        with open(
            os.path.dirname(__file__) + r"\text.json", "w", encoding="utf-8"
        ) as file:
            json.dump(text, file, indent=2, ensure_ascii=False)


class Hello_text:
    async def set_text(self, text):
        with open(
            os.path.dirname(__file__) + r"\hello.json", "w", encoding="utf-8"
        ) as file:
            json.dump(text, file, indent=2, ensure_ascii=False)


class MyCallback_choice(CallbackData, prefix="choice"):
    choice: Optional[str]


async def get_admin_menu():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Статистика", callback_data=MyCallback_choice(choice="1").pack()
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Рассылка", callback_data=MyCallback_choice(choice="2").pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Настройка текста под аудио",
            callback_data=MyCallback_choice(choice="3").pack(),
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Настройка текста для /start",
            callback_data=MyCallback_choice(choice="4").pack(),
        )
    )
    return builder


async def get_back():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Назад", callback_data=MyCallback_choice(choice="back").pack()
        )
    )
    return builder


@router.callback_query(MyCallback_choice.filter())
async def callback_for_music(
    query, callback_data: MyCallback_choice, state: FSMContext
):
    if callback_data.choice == "back":
        await state.clear()
        await query.message.edit_text(
            text="Это админ панель, выбери действие:",
            reply_markup=(await get_admin_menu()).as_markup(),
        )
    if callback_data.choice == "1":
        text = (
            f"Статистика:"
            f"\nПользователей всего: {(await database.get_all_users())}"
            f"\nНовых пользователей сегодня: {(await database.get_new_users())}"
            f"\nПользователей воспользовалось сегодня: {(await database.get_today_users())}"
            f"\n\nзапросов всего: {(await database.get_all_requests())}"
            f"\nзапросов сегодня: {(await database.get_today_requests())}"
        )
        await query.message.edit_text(
            text=text, reply_markup=(await get_back()).as_markup()
        )
    if callback_data.choice == "2":
        await query.message.edit_text(
            text="Пришлите ваш пост для рассылки:",
            reply_markup=(await get_back()).as_markup(),
        )
        await state.set_state(Get_post_state.get_post)
    if callback_data.choice == "3":
        await query.message.edit_text(
            text="Введите новый текст:", reply_markup=(await get_back()).as_markup()
        )
        await state.set_state(Get_text_state.get_text)
    if callback_data.choice == "4":
        await query.message.edit_text(
            text="Введите новый текст:", reply_markup=(await get_back()).as_markup()
        )
        await state.set_state(Get_text2_state.get_text)


@router.message(Get_text_state.get_text)
async def get_audio_text(message: Message, state: FSMContext, bot: Bot):
    res = {"text": message.text, "entities": []}
    if message.entities:
        for i in message.entities:
            res["entities"].append(
                {"type": i.type, "offset": i.offset, "length": i.length, "url": i.url}
            )

    await Audio_text().set_text(res)
    await message.answer("Готово!")
    await state.clear()


@router.message(Get_text2_state.get_text)
async def get_hello_text(message: Message, state: FSMContext, bot: Bot):
    res = {"text": message.text, "entities": []}
    if message.entities:
        for i in message.entities:
            res["entities"].append(
                {"type": i.type, "offset": i.offset, "length": i.length, "url": i.url}
            )

    await Hello_text().set_text(res)
    await message.answer("Готово!")
    await state.clear()


@router.message(Get_post_state.get_post)
async def get_mes_post(message: Message, state: FSMContext, bot: Bot):
    users = await database.get_users()
    count = 0
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user,
                message_id=message.message_id,
                from_chat_id=message.from_user.id,
                parse_mode="Markdown",
            )
        except Exception:
            pass
        else:
            count += 1
    await message.answer(
        f"Рассылка пришла {count} из {(await database.get_all_users())} пользователей!"
    )
    await state.clear()
