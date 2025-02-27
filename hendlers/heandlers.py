from aiogram import Router, types, F, Bot
from aiogram.types import Message
from aiogram.types import URLInputFile
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
import hendlers.playlists as pl
from typing import Optional
import json
import os

from API.smyslpesni import search
import DB.database as database
import hendlers.top as top
import hendlers.hrefs as hrefs

router = Router()


class Logs_group:
    async def get_group(self):
        with open(os.path.dirname(__file__) + r"\logs.json", encoding="utf-8") as file:
            self.data = json.load(file)
        return self.data


class Music:
    async def set_data(self, data):
        with open(os.path.dirname(__file__) + r"\music.json", "w") as file:
            json.dump(data, file, indent=2)

    async def get_data(self):
        with open(os.path.dirname(__file__) + r"\music.json") as file:
            self.data = json.load(file)
        return self.data


class Audio_text:
    async def get_text(self):
        with open(os.path.dirname(__file__) + r"\text.json", encoding="utf-8") as file:
            self.text = json.load(file)
        return self.text


class Last_mes:
    last_messages = {}

    async def get_last_messages(self):
        return self.last_messages

    async def set_last_messages(self, new):
        self.last_messages = new


class MyCallback_music(CallbackData, prefix="music"):
    id: Optional[int]
    tg_id: Optional[str]


class MyCallback_swipe(CallbackData, prefix="swipe"):
    action: Optional[str]
    page: Optional[int]


class MyCallback_add_playlist(CallbackData, prefix="add_playlist"):
    choice: Optional[str]


class MyCallback_add_music(CallbackData, prefix="add_music"):
    pl_id: Optional[int]


@router.message(F.text)
async def choice(message: Message):
    mes = await Last_mes().get_last_messages()
    if mes.get(str(message.from_user.id)) is not None:
        try:
            await mes.get(str(message.from_user.id)).message.delete()
        except Exception:
            try:
                await mes.get(str(message.from_user.id)).delete()
            except Exception:
                pass

    all_data = await search(message.text)
    all_music = all_data[0:10]
    bot_mes = None
    if all_music is None:
        bot_mes = await message.answer(
            "Не удалось обработать ваш запрос, попробуйте позднее"
        )
    elif len(all_music) == 0:
        bot_mes = await message.answer("Ничего не нашел, попробуйте изменить запрос")
    else:
        data = await Music().get_data()
        data[str(message.from_user.id)] = all_data
        await Music().set_data(data)
        builder = InlineKeyboardBuilder()
        for i in range(len(all_music)):
            builder.add(
                types.InlineKeyboardButton(
                    text=all_music[i].get("name"),
                    callback_data=MyCallback_music(
                        id=i, tg_id=str(message.from_user.id)
                    ).pack(),
                )
            )
        if len(all_data) > 10:
            builder.add(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=MyCallback_swipe(action="further", page=1).pack(),
                )
            )
        builder.adjust(1)
        bot_mes = await message.answer(
            "Выберите нужный трек:", reply_markup=builder.as_markup()
        )
    mes[str(message.from_user.id)] = bot_mes
    await Last_mes().set_last_messages(mes)


@router.callback_query(MyCallback_swipe.filter())
async def callback_for_music(query, callback_data: MyCallback_swipe):
    mes = await Last_mes().get_last_messages()
    mes[str(query.from_user.id)] = query
    await Last_mes().set_last_messages(mes)
    builder = InlineKeyboardBuilder()
    data = (await Music().get_data()).get(str(query.from_user.id))
    all_music = data[10 * callback_data.page : 10 * (callback_data.page + 1)]
    for i in range(len(all_music)):
        builder.row(
            types.InlineKeyboardButton(
                text=all_music[i].get("name"),
                callback_data=MyCallback_music(
                    id=(i + 10 * callback_data.page), tg_id=str(query.from_user.id)
                ).pack(),
            )
        )
    back = False
    if callback_data.page > 0:
        back = True
        builder.row(
            types.InlineKeyboardButton(
                text="⬅️",
                callback_data=MyCallback_swipe(
                    action="back", page=(callback_data.page - 1)
                ).pack(),
            )
        )
    if len(data) > (callback_data.page + 1) * 10:
        if back:
            builder.add(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=MyCallback_swipe(
                        action="further", page=(callback_data.page + 1)
                    ).pack(),
                )
            )
        else:
            builder.row(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=MyCallback_swipe(
                        action="further", page=(callback_data.page + 1)
                    ).pack(),
                )
            )
    await query.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(MyCallback_music.filter())
async def callback_for_music(query, callback_data: MyCallback_music, bot: Bot):
    mes = await Last_mes().get_last_messages()
    mes[str(query.from_user.id)] = query
    await Last_mes().set_last_messages(mes)

    all_data = await Music().get_data()
    text_data = await Audio_text().get_text()
    try:
        data = all_data[callback_data.tg_id][callback_data.id]
    except Exception:
        await query.message.delete()
        await query.message.answer("Ссылка истекла! Попробуйте повторить поиск")
        return
    entities = []

    for i in text_data["entities"]:
        entities.append(
            types.message_entity.MessageEntity(
                type=i["type"], offset=i["offset"], length=i["length"], url=i["url"]
            )
        )
    if len(entities) == 0:
        entities = None

    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Добавить в плейлист",
            callback_data=MyCallback_add_playlist(choice="1").pack(),
        )
    )

    have_cache = False
    href = data.get("href")
    cache = await hrefs.check_href(href)
    if cache is not None:
        audio = cache
        have_cache = True
    else:
        audio = URLInputFile(href)
    mes = await query.message.answer_audio(
        audio=audio,
        caption=text_data["text"],
        performer=data.get("artist"),
        title=data.get("title"),
        caption_entities=entities,
        reply_markup=builder.as_markup(),
    )

    if not have_cache:
        await hrefs.set_hrefs({href: mes.audio.file_id})
    await database.update_user_data(query.from_user.id)
    text = (
        f"Пользователь {query.message.chat.id} | {query.from_user.username} | {query.from_user.first_name} \n"
        f"искал песню {data.get('artist')} - {data.get('title')} \n"
        f"запросов всего - {await database.get_user_all_requests(query.message.chat.id)} \n"
        f"запросов сегодня - {await database.get_user_today_requests(query.message.chat.id)}"
    )

    log_group = (await Logs_group().get_group()).get("group_id")
    if log_group is not None:
        await bot.send_message(
            chat_id=log_group, text=text
        )

    await top.set_top(
        {
            "title": data.get("title"),
            "artist": data.get("artist"),
            "id": mes.audio.file_id,
        }
    )
    await query.answer(cache_time=10)


@router.callback_query(MyCallback_add_playlist.filter())
async def callback_get_playlists(query, callback_data: MyCallback_add_playlist):
    data = await pl.get_playlists()
    playlists = data.get(str(query.message.chat.id))
    if playlists is None:
        await query.message.answer(
            "У вас нет плейлистов! Создайте свой плейлист в главном меню!"
        )
        return

    builder = InlineKeyboardBuilder()
    for i in range(len(playlists)):
        builder.add(
            types.InlineKeyboardButton(
                text=playlists[i]["name"],
                callback_data=MyCallback_add_music(pl_id=i).pack(),
            )
        )

    await query.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(MyCallback_add_music.filter())
async def callback_get_playlists(query, callback_data: MyCallback_add_music):
    data = await pl.get_playlists()
    data[str(query.message.chat.id)][callback_data.pl_id]["songs"].append(
        {
            "id": query.message.audio.file_id,
            "artist": query.message.audio.performer,
            "title": query.message.audio.title,
        }
    )
    await pl.set_playlists(data)

    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Добавить в плейлист",
            callback_data=MyCallback_add_playlist(choice="1").pack(),
        )
    )

    await query.message.edit_reply_markup(reply_markup=builder.as_markup())
    await query.message.answer("Готово!")
