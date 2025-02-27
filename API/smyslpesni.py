from bs4 import BeautifulSoup
import fake_useragent
import aiohttp
import asyncio


# поиск по запросу юзера
async def search(data: str) -> list | None:
    url = "https://smyslpesni.ru/music/" + data
    headers = {"user-agent": fake_useragent.UserAgent().random}
    res = None

    # Отправляем запрос
    async with aiohttp.ClientSession() as session:
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with session.get(url, headers=headers, timeout=timeout) as get:
                res = await get.text()
        except asyncio.TimeoutError:
            return None

    soup = BeautifulSoup(res, "lxml")

    try:
        soup = soup.find("div", class_="sect-col track-list").find_all(
            "div", class_="sect-col__item fx-row fx-middle js-item track-item"
        )
    except AttributeError:
        return []

    resault = []
    for i in soup:
        name = i["data-meta-title"]
        href = "https:" + i["data-file"]
        title = i["data-track-title"]
        artist = i["data-artist"]

        dict = {"name": name, "href": href, "title": title, "artist": artist}
        resault.append(dict)

    return resault


if __name__ == "__main__":
    search("я ебу собак")
