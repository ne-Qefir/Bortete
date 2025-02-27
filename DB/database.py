import sqlite3
import os
from datetime import date


# функция регистрации нового пользователя
async def register_user(tg_id: int, number_of_requests: int = 0) -> None:
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM Users WHERE tg_id = ?", (tg_id,))
        data = cur.fetchone()

        if data is None:
            cur.execute(
                "INSERT INTO Users(tg_id, number_of_requests, joined, number_of_requests_today) VALUES(?, ?, ?, ?);",
                (tg_id, number_of_requests, date.today(), 0),
            )
            conn.commit()

        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# функция обновления информации о пользователи
async def update_user_data(tg_id: int) -> None:
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()

        cur.execute("SELECT last_request FROM Users WHERE tg_id = ?", (tg_id,))
        last_request = cur.fetchone()[0]
        if last_request == str(date.today()):
            cur.execute(
                "SELECT number_of_requests_today FROM Users WHERE tg_id = ?", (tg_id,)
            )
            number_of_requests_today = cur.fetchone()[0]

            cur.execute(
                "UPDATE Users SET last_request = ?, number_of_requests_today = ? where tg_id = ?",
                (
                    date.today(),
                    int(number_of_requests_today) + 1,
                    tg_id,
                ),
            )
        else:
            cur.execute(
                "UPDATE Users SET last_request = ?, number_of_requests_today = ? where tg_id = ?",
                (
                    date.today(),
                    1,
                    tg_id,
                ),
            )
        conn.commit()

        cur.execute("SELECT number_of_requests FROM Users WHERE tg_id = ?", (tg_id,))
        number_of_requests = cur.fetchone()[0]

        cur.execute(
            "UPDATE Users SET last_request = ?, number_of_requests = ? where tg_id = ?",
            (
                date.today(),
                int(number_of_requests) + 1,
                tg_id,
            ),
        )
        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получение количества запросов за все время
async def get_all_requests() -> int:
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()

        cur.execute("SELECT number_of_requests FROM Users")
        number_of_requests = cur.fetchall()
        count = 0

        for i in number_of_requests:
            if i[0] is None:
                return 0
            count += int(i[0])

        return count
        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получение количества запросов за сегодня
async def get_today_requests() -> int:
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT number_of_requests_today FROM Users WHERE last_request = ?",
            (date.today(),),
        )
        number_of_requests = cur.fetchall()
        count = 0

        for i in number_of_requests:
            if i[0] is None:
                return 0
            count += int(i[0])

        return count
        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# обновляем все тг айди админов из txt
async def update_admins():
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        with open(os.path.dirname(__file__) + r"\admins.txt", "r") as file:
            admins = file.readlines()
            for tg_id in admins:
                cur.execute("SELECT tg_id FROM Admins WHERE tg_id = ?", (tg_id,))
                if cur.fetchone() is None:
                    cur.execute(
                        "INSERT INTO Admins(tg_id) VALUES(?);",
                        (tg_id,),
                    )

        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем все тг айди админов
async def get_admin():
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM Admins")
        all_id = cur.fetchall()
        conn.commit()
        cur.close()

        resault = []
        for i in all_id:
            resault.append(i[0])
        return resault

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем все тг айди юзеров
async def get_users():
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM Users")
        all_id = cur.fetchall()
        conn.commit()
        cur.close()

        resault = []
        for i in all_id:
            resault.append(i[0])
        return resault

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем сегодняшних юзеров из бд
async def get_today_users() -> int:
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM Users WHERE last_request = ?", (date.today(),))

        count = len(cur.fetchall())

        if count is None:
            return 0
        else:
            return count

        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем всех юзеров из бд
async def get_all_users() -> int:
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM Users")

        count = len(cur.fetchall())

        if count is None:
            return 0
        else:
            return count

        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем колво запросов юзера
async def get_user_all_requests(tg_id) -> int:
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT number_of_requests FROM Users WHERE tg_id = ?", (tg_id,))

        return cur.fetchone()[0]

        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем колво запросов юзера
async def get_user_today_requests(tg_id) -> int:
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT number_of_requests_today FROM Users WHERE tg_id = ? AND last_request = ?",
            (tg_id, date.today()),
        )

        res = cur.fetchone()
        if res[0] is None:
            return 0
        else:
            return res[0]

        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()


# получаем всех юзеров из бд
async def get_new_users() -> int:
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(__file__) + r"\Users.db")
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM Users WHERE joined = ?", (date.today(),))

        count = len(cur.fetchall())

        if count is None:
            return 0
        else:
            return count

        conn.commit()
        cur.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if conn:
            conn.close()
