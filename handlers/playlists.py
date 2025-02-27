import json
import os


async def set_playlists(data: dict):
    with open(os.path.dirname(__file__) + r"\playlist.json", "w") as file:
        json.dump(data, file, indent=2)


async def get_playlists() -> dict:
    data = None
    with open(os.path.dirname(__file__) + r"\playlist.json") as file:
        data = json.load(file)
    return data
