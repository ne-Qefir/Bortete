from aiogram import Router, types, Bot
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from typing import Optional
import os
import json

import DB.database as database
import hendlers.playlists as pl
import hendlers.top as top

router = Router()


class playlist_name_state(StatesGroup):
    get_name = State()


class Audio_text:
    async def get_text(self):
        with open(os.path.dirname(__file__) + r"\text.json", encoding="utf-8") as file:
            self.text = json.load(file)
        return self.text


class Hello_text:
    async def get_text(self):
        with open(os.path.dirname(__file__) + r"\hello.json", encoding="utf-8") as file:
            self.text = json.load(file)
        return self.text


class MyCallback_user_choice(CallbackData, prefix="user_choice"):
    choice: Optional[str]
    tg_id: Optional[str]


class MyCallback_playlist(CallbackData, prefix="playlist"):
    pl_id: Optional[str]


class MyCallback_del_playlist(CallbackData, prefix="del_playlist"):
    pl_id: Optional[int]


class MyCallback_get_music(CallbackData, prefix="get_music"):
    pl_id: Optional[int]
    id: Optional[int]


class MyCallback_del_song(CallbackData, prefix="choose_del_music"):
    pl_id: Optional[int]


class MyCallback_del_choosing_music(CallbackData, prefix="del_music"):
    pl_id: Optional[int]
    id: Optional[int]


class MyCallback_top(CallbackData, prefix="get_page"):
    page: Optional[int]
    action: Optional[str]


class MyCallback_get_top_music(CallbackData, prefix="top_page"):
    id: Optional[int]


# Хэндлер на /start
@router.message(Command("start"))
async def start(message: Message):
    await database.register_user(message.from_user.id)
    data = await Hello_text().get_text()
    entities = []

    for i in data["entities"]:
        entities.append(
            types.message_entity.MessageEntity(
                type=i["type"], offset=i["offset"], length=i["length"], url=i["url"]
            )
        )
    if len(entities) == 0:
        entities = None

    await message.answer_photo(
        photo="AgACAgIAAxkBAAMKZLz9zT3MXRYoFCd4zufYUtWjXngAAqHKMRt1HOlJlO7fzKkFgnEBAAMCAAN5AAMvBA",
        caption=data["text"],
        reply_markup=(await get_menu()).as_markup(),
        entities=entities,
    )


@router.message(Command("random"))
async def random(message: Message):
    data = await top.get_random_song()
    text_data = await Audio_text().get_text()
    entities = []

    for i in text_data["entities"]:
        entities.append(
            types.message_entity.MessageEntity(
                type=i["type"], offset=i["offset"], length=i["length"], url=i["url"]
            )
        )
    if len(entities) == 0:
        entities = None

    await message.answer_audio(
        audio=data["id"],
        performer=data["artist"],
        title=data["title"],
        caption=text_data["text"],
        caption_entities=entities,
    )


async def get_menu():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Информация", callback_data=MyCallback_user_choice(choice="1").pack()
        )
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Плейлисты", callback_data=MyCallback_user_choice(choice="2").pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Топ", callback_data=MyCallback_user_choice(choice="3").pack()
        )
    )
    return builder


async def get_menu_back():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Назад", callback_data=MyCallback_user_choice(choice="back").pack()
        )
    )
    return builder


async def get_playlists_menu(tg_id):
    playlists = (await pl.get_playlists()).get(str(tg_id))

    builder = InlineKeyboardBuilder()
    if playlists is not None:
        for i in range(len(playlists)):
            builder.row(
                types.InlineKeyboardButton(
                    text=playlists[i]["name"],
                    callback_data=MyCallback_playlist(pl_id=i).pack(),
                )
            )

    builder.row(
        types.InlineKeyboardButton(
            text="создать плейлист",
            callback_data=MyCallback_playlist(pl_id="new").pack(),
        ),
    )
    builder.add(
        types.InlineKeyboardButton(
            text="удалить плейлист",
            callback_data=MyCallback_playlist(pl_id="del").pack(),
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад", callback_data=MyCallback_user_choice(choice="back").pack()
        ),
    )

    return builder


async def get_playlists_back():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=MyCallback_user_choice(choice="back2").pack(),
        )
    )
    return builder


@router.callback_query(MyCallback_user_choice.filter())
async def callback_user_choice(
    query, callback_data: MyCallback_user_choice, state: FSMContext
):
    await query.message.delete()
    if callback_data.choice == "back":
        await state.clear()
        data = await Hello_text().get_text()
        entities = []

        for i in data["entities"]:
            entities.append(
                types.message_entity.MessageEntity(
                    type=i["type"], offset=i["offset"], length=i["length"], url=i["url"]
                )
            )
        if len(entities) == 0:
            entities = None

        await query.message.answer_photo(
            photo="AgACAgIAAxkBAAMKZLz9zT3MXRYoFCd4zufYUtWjXngAAqHKMRt1HOlJlO7fzKkFgnEBAAMCAAN5AAMvBA",
            caption=data["text"],
            entities=entities,
            reply_markup=(await get_menu()).as_markup(),
        )

    if callback_data.choice == "back2":
        await state.clear()
        await query.message.answer(
            text="Ваши плейлисты:",
            reply_markup=(await get_playlists_menu(query.message.chat.id)).as_markup(),
        )

    if callback_data.choice == "1":
        text = (
            f"Информация:"
            f"\nДля использования бота просто введи название любой песни"
            f"\n\nИногда бот может не находить ваши песни. "
            f"\nПопробуйте снова, меняя регистр 1ой буквы"
            f"\nили написав автора/название трека на оригинальном языке"
            f"\n\nРандомная песня:"
            f"\nДля получение рандомной песни введи /random"
            f"\n\nТоп:"
            f"\nТоп песен составляется из самых частых запросов пользователей!"
            f"\n\nПлейлисты:"
            f"\nВ главном меню вы можете создать свои плейлисты"
            f"\nКогда бот отправляет вам трек, вы можете добавить его в свои плейлисты!"
            f"\n\nКак скачать трек на устройство:"
            f"\nДля скачивания трека нажмите на значок загрузки на кнопке проигрования"
            f"\nЛибо зажмите/нажмите на пкм на треке для появления меню, где можно загрузить трек!"
        )
        await query.message.answer(
            text=text, reply_markup=(await get_menu_back()).as_markup()
        )

    if callback_data.choice == "2":
        builder = await get_playlists_menu(query.message.chat.id)
        await query.message.answer(
            text=f"Ваши плейлисты:", reply_markup=builder.as_markup()
        )

    if callback_data.choice == "3":
        text = f"Топ песен по запрсам:"
        data = await top.get_famous_top()
        builder = InlineKeyboardBuilder()
        songs = data[0:10]
        for i in range(len(songs)):
            builder.row(
                types.InlineKeyboardButton(
                    text=f"{songs[i].get('artist')} - {songs[i].get('title')}",
                    callback_data=MyCallback_get_top_music(id=i).pack(),
                )
            )
        if len(data) > 10:
            builder.row(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=MyCallback_top(action="further", page=1).pack(),
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text="Назад", callback_data=MyCallback_user_choice(choice="back").pack()
            )
        )

        await query.message.answer(text=text, reply_markup=builder.as_markup())


@router.callback_query(MyCallback_get_top_music.filter())
async def callback_for_top_music(query, callback_data: MyCallback_get_top_music):
    data = (await top.get_famous_top())[callback_data.id]
    text_data = await Audio_text().get_text()
    entities = []

    for i in text_data["entities"]:
        entities.append(
            types.message_entity.MessageEntity(
                type=i["type"], offset=i["offset"], length=i["length"], url=i["url"]
            )
        )
    if len(entities) == 0:
        entities = None

    await top.set_top(
        {
            "title": data.get("title"),
            "artist": data.get("artist"),
            "id": data.get("id"),
        }
    )

    await query.message.answer_audio(
        audio=data["id"],
        performer=data["artist"],
        title=data["title"],
        caption=text_data["text"],
        caption_entities=entities,
    )


@router.callback_query(MyCallback_top.filter())
async def callback_for_top_music(query, callback_data: MyCallback_top):
    builder = InlineKeyboardBuilder()
    data = await top.get_famous_top()
    all_music = data[10 * callback_data.page : 10 * (callback_data.page + 1)]
    for i in range(len(all_music)):
        builder.row(
            types.InlineKeyboardButton(
                text=f"{all_music[i].get('artist')} - {all_music[i].get('title')}",
                callback_data=MyCallback_get_top_music(
                    id=i + (callback_data.page * 10)
                ).pack(),
            )
        )
    back = False
    if callback_data.page > 0:
        back = True
        builder.row(
            types.InlineKeyboardButton(
                text="⬅️",
                callback_data=MyCallback_top(
                    action="back", page=(callback_data.page - 1)
                ).pack(),
            )
        )
    if len(data) > (callback_data.page + 1) * 10:
        if back:
            builder.add(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=MyCallback_top(
                        action="further", page=(callback_data.page + 1)
                    ).pack(),
                )
            )
        else:
            builder.row(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=MyCallback_top(
                        action="further", page=(callback_data.page + 1)
                    ).pack(),
                )
            )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад", callback_data=MyCallback_user_choice(choice="back").pack()
        )
    )
    await query.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(MyCallback_playlist.filter())
async def callback_playlist(
    query, callback_data: MyCallback_playlist, state: FSMContext
):
    if callback_data.pl_id == "new":
        await query.message.edit_text("Введите название плейлиста:")
        await state.set_state(playlist_name_state.get_name)

    elif callback_data.pl_id == "del":
        playlists = (await pl.get_playlists()).get(str(query.message.chat.id))
        if playlists is None:
            await query.message.answer("У вас нет плейлистов!")
            return
        if len(playlists) == 0:
            await query.message.answer("У вас нет плейлистов!")
            return
        builder = InlineKeyboardBuilder()
        for i in range(len(playlists)):
            builder.row(
                types.InlineKeyboardButton(
                    text=playlists[i]["name"],
                    callback_data=MyCallback_del_playlist(pl_id=i).pack(),
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=MyCallback_user_choice(choice="back2").pack(),
            )
        )
        await query.message.edit_text(
            "Выберите плейлист для удаления:", reply_markup=builder.as_markup()
        )

    else:
        playlist = (await pl.get_playlists())[str(query.message.chat.id)][
            int(callback_data.pl_id)
        ]
        builder = InlineKeyboardBuilder()
        for i in range(len(playlist["songs"])):
            builder.row(
                types.InlineKeyboardButton(
                    text=f"{playlist['songs'][i]['artist']} - {playlist['songs'][i]['title']}",
                    callback_data=MyCallback_get_music(
                        id=i, pl_id=int(callback_data.pl_id)
                    ).pack(),
                )
            )

        builder.row(
            types.InlineKeyboardButton(
                text="Удалить трек",
                callback_data=MyCallback_del_song(
                    pl_id=int(callback_data.pl_id)
                ).pack(),
            )
        )

        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=MyCallback_user_choice(choice="back2").pack(),
            )
        )

        await query.message.edit_text(
            f"Треки в плейлисте {playlist['name']}:", reply_markup=builder.as_markup()
        )


@router.callback_query(MyCallback_del_song.filter())
async def callback_choose_del_music(query, callback_data: MyCallback_del_song):
    builder = InlineKeyboardBuilder()
    playlist = (await pl.get_playlists())[str(query.message.chat.id)][
        callback_data.pl_id
    ]
    for i in range(len(playlist["songs"])):
        builder.row(
            types.InlineKeyboardButton(
                text=f"{playlist['songs'][i]['artist']} - {playlist['songs'][i]['title']}",
                callback_data=MyCallback_del_choosing_music(
                    id=i, pl_id=callback_data.pl_id
                ).pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=MyCallback_playlist(pl_id=callback_data.pl_id).pack(),
        )
    )
    await query.message.edit_text(
        text="Выбери трек для удаления:", reply_markup=builder.as_markup()
    )


@router.callback_query(MyCallback_del_choosing_music.filter())
async def callback_del_music(query, callback_data: MyCallback_del_choosing_music):
    data = await pl.get_playlists()
    data[str(query.message.chat.id)][callback_data.pl_id]["songs"].pop(callback_data.id)
    await pl.set_playlists(data)
    keyboard = query.message.reply_markup
    keyboard.inline_keyboard = [keyboard.inline_keyboard[-1]]
    await query.message.edit_text("Трек удален!", reply_markup=keyboard)


@router.message(playlist_name_state.get_name)
async def get_name(message: Message, state: FSMContext, bot: Bot):
    data = await pl.get_playlists()
    playlists = data.get(str(message.from_user.id))
    if playlists is None:
        playlists = []

    playlists.append({"name": message.text, "songs": []})
    data[str(message.from_user.id)] = playlists
    await pl.set_playlists(data)
    await message.answer(
        "Готово!", reply_markup=(await get_playlists_back()).as_markup()
    )


@router.callback_query(MyCallback_get_music.filter())
async def callback_get_music(
    query, callback_data: MyCallback_get_music, state: FSMContext
):
    data = (await pl.get_playlists())[str(query.message.chat.id)][callback_data.pl_id][
        "songs"
    ][callback_data.id]

    await query.message.answer_audio(
        audio=data["id"],
        performer=data["artist"],
        title=data["title"],
    )


@router.callback_query(MyCallback_del_playlist.filter())
async def callback_add_music(query, callback_data: MyCallback_del_playlist):
    data = await pl.get_playlists()
    data[str(query.message.chat.id)].pop(callback_data.pl_id)
    await pl.set_playlists(data)
    await query.message.edit_text(
        "Готово!",
        reply_markup=(await get_playlists_menu(query.message.chat.id)).as_markup(),
    )
