import json
import os


async def set_hrefs(data):
    hrefs = await get_href()
    with open(os.path.dirname(__file__) + r"\hrefs.json", "w") as file:
        res = hrefs | data
        json.dump(res, file, indent=2)


async def get_href():
    with open(os.path.dirname(__file__) + r"\hrefs.json") as file:
        data = json.load(file)
    return data


async def check_href(href):
    with open(os.path.dirname(__file__) + r"\hrefs.json") as file:
        data = json.load(file)
    return data.get(href)
