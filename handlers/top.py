import json
import os
import random
import emoji
from jellyfish import jaro_winkler_similarity as jf


async def set_top(text):
    text["artist"] = emoji.replace_emoji(text["artist"], replace="")
    text["title"] = emoji.replace_emoji(text["title"], replace="")

    data = (await get_top()).get("songs")

    Add_song = True

    for i in range(len(data)):
        if (
            jf(data[i]["artist"], text["artist"]) >= 0.90
            and jf(data[i]["title"], text["title"]) > 0.8
        ):
            data[i]["requests"] += 1
            Add_song = False
            break

    if Add_song:
        text["requests"] = 1
        data.append(text)

    with open(os.path.dirname(__file__) + r"\top.json", "w") as file:
        json.dump({"songs": data}, file, indent=2)


async def get_top():
    with open(os.path.dirname(__file__) + r"\top.json") as file:
        data = json.load(file)
    return data


async def get_famous_top():
    with open(os.path.dirname(__file__) + r"\top.json") as file:
        data = json.load(file)
        data = sorted_list = sorted(data["songs"], key=lambda x: x["requests"])[::-1]
    return data[0:100]


async def get_random_song():
    with open(os.path.dirname(__file__) + r"\top.json") as file:
        data = json.load(file)
    return data["songs"][random.randint(0, len(data["songs"]) - 1)]
