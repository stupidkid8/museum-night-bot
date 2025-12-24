import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

API_TOKEN = "8441700443:AAEuMOkI5zeIC015y8hxng4i5rLqWAPWbKU"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# user_id -> данные опроса
answers: dict[int, dict] = {}

# ---------- КЛАВИАТУРЫ ----------

kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Что такое ночь музеев?")],
        [KeyboardButton(text="Расскажи про все мероприятия."),
         KeyboardButton(text="Хочу посмотреть фильтры.")],
        [KeyboardButton(text="Составь мое расписание")],
    ],
    resize_keyboard=True
)

kb_about = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True
)

kb_company = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Иду один")],
        [KeyboardButton(text="Один, я интроверт")],
        [KeyboardButton(text="Иду в компании (взрослые)")],
        [KeyboardButton(text="Иду в компании (школьники)")],
        [KeyboardButton(text="Иду с маленьким ребёнком")],
        [KeyboardButton(text="Идём с парой")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True
)

kb_age = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Взрослые 30+")],
        [KeyboardButton(text="Студенты 18+")],
        [KeyboardButton(text="Школьники 13–17")],
        [KeyboardButton(text="Микс-компания")],
        [KeyboardButton(text="Микс-компания с ребёнком")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True
)

kb_activity = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Экскурсии"), KeyboardButton(text="Квесты")],
        [KeyboardButton(text="Интеллектуальные лекции")],
        [KeyboardButton(text="Мастер-классы")],
        [KeyboardButton(text="Смотреть кино")],
        [KeyboardButton(text="Изучать технологии")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True
)

kb_plan_actions = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Концерт в Конторе")],
        [KeyboardButton(text="Квест в Словцова")],
        [KeyboardButton(text="Выставка в Колокольникова")],
        [KeyboardButton(text="Далее")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True
)

# ---------- СЦЕНАРИИ ----------

COMPANY_OPTIONS = [
    "Иду один",
    "Один, я интроверт",
    "Иду в компании (взрослые)",
    "Иду в компании (школьники)",
    "Иду с маленьким ребёнком",
    "Идём с парой",
]

AGE_OPTIONS = [
    "Взрослые 30+",
    "Студенты 18+",
    "Школьники 13–17",
    "Микс-компания",
    "Микс-компания с ребёнком",
]

ACTIVITY_OPTIONS = [
    "Экскурсии",
    "Квесты",
    "Интеллектуальные лекции",
    "Мастер-классы",
    "Смотреть кино",
    "Изучать технологии",
]

# ---------- ХЕНДЛЕРЫ ----------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = (
        "Привет, я бот мероприятия Ночь музеев!\n"
        "Встречаемся 13.06 | СБ\n"
        "Расскажи, как я могу помочь?"
    )
    await message.answer(text, reply_markup=kb_main)


@dp.message(lambda m: m.text == "Что такое ночь музеев?")
async def about(message: types.Message):
    await message.answer(
        "«Ночь музеев» — это международная ежегодная культурная акция, когда музеи, галереи "
        "и другие культурные учреждения работают в вечерние и ночные часы и делают спецпрограмму: "
        "экскурсии, концерты, мастер‑классы и т.д.\n\n"
        "Хочешь — в главном меню можно составить персональное расписание.",
        reply_markup=kb_about
    )


@dp.message(lambda m: m.text == "🔙 Назад")
async def back_from_about(message: types.Message):
    await message.answer(
        "Ок, возвращаемся в главное меню. Чем могу помочь?",
        reply_markup=kb_main
    )


@dp.message(lambda m: m.text == "🔙 В меню")
async def back_to_menu(message: types.Message):
    await message.answer(
        "Ок, возвращаемся в главное меню.",
        reply_markup=kb_main
    )


@dp.message(lambda m: m.text == "Составь мое расписание")
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    answers[user_id] = {"company": None, "age": None, "activities": []}
    await message.answer(
        "Хорошо, давай подберём тебе маршрут. В какой компании ты идёшь?",
        reply_markup=kb_company
    )


@dp.message(lambda m: m.text in COMPANY_OPTIONS)
async def ask_age(message: types.Message):
    user_id = message.from_user.id
    answers.setdefault(user_id, {"company": None, "age": None, "activities": []})
    answers[user_id]["company"] = message.text
    await message.answer(
        "Сколько лет тебе (и тем, кто пойдёт с тобой, если вы идёте вместе)?",
        reply_markup=kb_age
    )


@dp.message(lambda m: m.text in AGE_OPTIONS)
async def ask_activity(message: types.Message):
    user_id = message.from_user.id
    answers.setdefault(user_id, {"company": None, "age": None, "activities": []})
    answers[user_id]["age"] = message.text
    await message.answer(
        "Что ты хочешь делать в Ночь музеев? (можно выбрать несколько пунктов по очереди).\n"
        "Когда закончишь выбор, напиши 'Готово'.",
        reply_markup=kb_activity
    )


@dp.message(lambda m: m.text in ACTIVITY_OPTIONS)
async def collect_activities(message: types.Message):
    user_id = message.from_user.id
    answers.setdefault(user_id, {"company": None, "age": None, "activities": []})
    if message.text not in answers[user_id]["activities"]:
        answers[user_id]["activities"].append(message.text)
    await message.answer(
        f"Ок, добавляю: {message.text}. Можешь выбрать ещё или написать 'Готово'."
    )


@dp.message(lambda m: (m.text or "").strip().lower() == "готово")
async def finish_quiz(message: types.Message):
    user_id = message.from_user.id
    data = answers.get(user_id)

    if not data:
        await message.answer(
            "Пока нет данных. Нажми «Составь мое расписание» и пройди мини-опрос.",
            reply_markup=kb_main
        )
        return

    company = data.get("company") or "не указано"
    age = data.get("age") or "не указано"
    activities = data.get("activities") or ["не выбрано"]
    activities_text = ", ".join(activities)

    await message.answer(
        "Супер, вот что я про тебя понял:\n"
        f"• Компания: {company}\n"
        f"• Возраст/тип компании: {age}\n"
        f"• Любимые активности: {activities_text}\n",
        reply_markup=kb_main
    )

    schedule_text = (
        "Лови своё расписание на Ночь музеев:\n\n"
        "20:00–20:30 — Контора Пароходства (ул. 25 лет Октября 23): концерт группы Биофакс.\n"
        "Далее: 12 минут пешком (≈5 минут на самокате).\n\n"
        "20:45–21:15 — музей им. Словцова (ул. Советская 63): квест по современному искусству.\n"
        "Далее: 15 минут пешком (≈7 минут на самокате).\n\n"
        "21:35–22:30 — музей им. Колокольникова (ул. Республики 56): выставка.\n\n"
        "Точки маршрута отмечены на карте ниже."
    )

    await message.answer(schedule_text, reply_markup=kb_plan_actions)

    # базовая карта маршрута
    await message.answer_photo(FSInputFile("map.jpg"))


@dp.message(lambda m: m.text == "Концерт в Конторе")
async def action_kontora(message: types.Message):
    await message.answer(
        "Концерт в Конторе Пароходства: приходи чуть раньше, чтобы занять места."
    )


@dp.message(lambda m: m.text == "Квест в Словцова")
async def action_slovtsov(message: types.Message):
    await message.answer(
        "Квест в музее им. Словцова: будь на месте за 10 минут, чтобы зарегистрироваться."
    )


@dp.message(lambda m: m.text == "Выставка в Колокольникова")
async def action_kolok(message: types.Message):
    await message.answer(
        "Выставка в музее им. Колокольникова: можно приходить в любое время в указанном интервале."
    )


@dp.message(lambda m: m.text == "Далее")
async def after_route(message: types.Message):
    await message.answer(
        "Если захочешь сделать паузу после маршрута, на этой карте отмечены дополнительные точки рядом.\n\n"
        "Подробнее о точке на карте: https://go.2gis.com/4WwnM"
    )
    await message.answer_photo(FSInputFile("map_cafe.jpg"))


@dp.message(lambda m: m.text == "Расскажи про все мероприятия.")
async def all_events(message: types.Message):
    text = (
        "Кратко про события в Тюмени в декабре:\n\n"
        "• Концерты и шоу – новогодние программы.\n"
        "• Театр – детские и взрослые спектакли.\n"
        "• Выставки и ярмарки – городские площадки.\n\n"
        "Подробности смотри на афишных сайтах города."
    )
    await message.answer(text)


@dp.message(lambda m: m.text == "Хочу посмотреть фильтры.")
async def filters(message: types.Message):
  await message.answer(
        "Фильтры, по которым дальше можно будет подбирать мероприятия:\n\n"
        "• По времени: начать раньше 20:00 или позже 21:00; короткие события (до 40 минут) "
        "или длинные (1–1,5 часа); форматы, куда можно зайти в любой момент.\n\n"
        "• По месту: события в центре (Словцова, Колокольников, набережная, Контора Пароходства) "
        "и площадки в пешей доступности друг от друга.\n\n"
        "• По формату: камерные или массовые события; где можно спокойно сидеть "
        "или нужно ходить и исследовать; форматы с разговорами и обсуждениями "
        "или акцентом на музыке и просмотре."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
