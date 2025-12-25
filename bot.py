import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton
)

BOT_TOKEN = os.getenv("8441700443:AAEuMOkI5zeIC015y8hxng4i5rLqWAPWbKU")

EVENTS_TYUMEN_LINK = os.getenv("EVENTS_TYUMEN_LINK", "https://afisha.yandex.ru/tyumen")
FEEDBACK_LINK = os.getenv(
    "FEEDBACK_LINK",
    "https://docs.google.com/forms/d/e/1FAIpQLScoJVHvACWSvIYTplt0dEAey1wGLFb15hcl4lh6pYmyE-ONFw/viewform?usp=dialog",
)

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    raise RuntimeError("Укажи BOT_TOKEN в окружении: export BOT_TOKEN='...'")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# user_id -> данные опроса
answers: dict[int, dict] = {}

# =========================
# EVENTS (для фильтров)
# =========================
EVENTS = {
    "🎄 Открытие главной городской ёлки (27 декабря)": {
        "title": "🎄 Открытие главной городской ёлки",
        "time": "27 декабря 2025, 17:00",
        "address": "площадь 400‑летия Тюмени",
        "format": "уличное праздничное шоу",
        "price": "0 ₽ (бесплатно)",
    },
    "🚜 Новогодний тракторный кортеж (26–27 декабря)": {
        "title": "🚜 Новогодний тракторный кортеж",
        "time": "26 декабря 2025 (ул. Фармана Салманова, 2, 18:00); 27 декабря 2025 (пл. 400‑летия Тюмени, ул. Республики 129)",
        "address": "старт от катка «Сердце Тюмени», движение по улицам города",
        "format": "парад украшенной техники",
        "price": "0 ₽ (бесплатно)",
    },
    "🎭 Мюзикл «Ночь перед Рождеством»": {
        "title": "🎭 Мюзикл «Ночь перед Рождеством»",
        "time": "27 декабря 2025, 14:00",
        "address": "Тюменский Большой драматический театр",
        "format": "мюзикл для всей семьи",
        "price": "от 600 ₽",
    },
    "🎵 Новогодний ретро-концерт «Песня года»": {
        "title": "🎵 Новогодний ретро-концерт «Песня года»",
        "time": "27 декабря 2025",
        "address": "Дворец культуры «Нефтяник» им. В. И. Муравленко",
        "format": "ретро-концерт",
        "price": "от 600 ₽",
    },
    "🐌 Гастротур на улиточную ферму (28 декабря)": {
        "title": "🐌 Гастротур на улиточную ферму",
        "time": "28 декабря 2025, 11:00",
        "address": "место сбора — парковка отеля «Восток» или ул. Республики (уточняется при покупке)",
        "format": "экскурсия с дегустацией",
        "price": "от 1 300 ₽",
    },
    "🧸 Спектакль «Красавица и Чудовище»": {
        "title": "🧸 Спектакль «Красавица и Чудовище» (театр кукол)",
        "time": "27 декабря 2025, 10:00, 12:30, 15:00",
        "address": "Тюменский театр кукол",
        "format": "кукольный спектакль",
        "price": "от 600 ₽",
    },
    "💿 Трибьют «Забытые пластинки»": {
        "title": "💿 Трибьют-концерт «Забытые пластинки. От Варум до Булановой»",
        "time": "28 декабря 2025, 20:00 (или 19:00)",
        "address": "коктейль-бар «Майлз», ул. Республики, 42",
        "format": "трибьют-концерт",
        "price": "от 1 200 ₽",
    },
    "🎪 Проект «Погружение в театр»": {
        "title": "🎪 Проект «Погружение в театр» (экскурсия за кулисы)",
        "time": "27 декабря 2025, 19:00",
        "address": "Тюменский большой драматический театр (ТБДТ), Большой зал, фойе",
        "format": "экскурсия за кулисы",
        "price": "от 3 000 ₽",
    },
    "🎻 Concord Orchestra — Штраус (23 декабря)": {
        "title": "🎻 Concord Orchestra. Белоснежный бал Иоганна Штрауса",
        "time": "23 декабря 2025, 19:00",
        "address": "Дворец культуры «Нефтяник»",
        "format": "симфоническое шоу",
        "price": "от 1 000 ₽ (ориентировочно)",
    },
    "🎪 Цирковое шоу «Алиса…»": {
        "title": "🎪 Цирковое шоу «Алиса в Зазеркалье новогодних чудес»",
        "time": "24 декабря 2025, 17:00",
        "address": "Дворец творчества и спорта «Пионер»",
        "format": "цирковой спектакль",
        "price": "от 500 ₽ (ориентировочно)",
    },
    "🎅 Резиденция Деда Мороза (Кристалл)": {
        "title": "🎅 Резиденция Деда Мороза в ТРЦ «Кристалл»",
        "time": "25–30 декабря 2025, по будням 18:00–20:00, в выходные 17:00–20:00",
        "address": "ТРЦ «Кристалл», 1 этаж",
        "format": "интерактивная площадка",
        "price": "0 ₽ (бесплатно)",
    },
    "🎸 Pink Floyd (Floyd Universe) (4 января)": {
        "title": "🎸 Pink Floyd – легендарные хиты в исполнении группы Floyd Universe",
        "time": "4 января 2026, 18:00",
        "address": "Дворец культуры «Нефтяник», Большой зал",
        "format": "трибьют-шоу с симфоническим оркестром",
        "price": "от 2 400 ₽",
    },
    "🐱 Волшебные кошки Куклачева (2 января)": {
        "title": "🐱 Волшебные кошки Куклачева",
        "time": "2 января 2026, 12:00 и 15:00",
        "address": "ДК «Железнодорожник», ул. Первомайская, 55",
        "format": "шоу театра кошек",
        "price": "от 1 200 ₽",
    },
    "🎭 Не стреляйте в экстрасенса (6 января)": {
        "title": "🎭 Не стреляйте в экстрасенса",
        "time": "6 января 2026, 18:00",
        "address": "Дворец культуры «Нефтяник»",
        "format": "комедийный спектакль",
        "price": "от 1 500 ₽",
    },
    "👑 Radio Queen + симфонический оркестр (3 января)": {
        "title": "👑 Radio Queen с симфоническим оркестром: Шоу «Богемская рапсодия»",
        "time": "3 января 2026, 18:00",
        "address": "Дворец культуры «Нефтяник», Большой зал",
        "format": "трибьют-шоу",
        "price": "от 2 800 ₽",
    },
}

# =========================
# FILTER HELPERS
# =========================
def normalize_price_to_int(price_str: str) -> int | None:
    digits = "".join(ch for ch in price_str if ch.isdigit())
    return int(digits) if digits else None


def event_date_key(time_str: str) -> str:
    t = time_str.lower()
    if "23 декабря 2025" in t:
        return "23.12.2025"
    if "24 декабря 2025" in t:
        return "24.12.2025"
    if "25–30 декабря 2025" in t or "25-30 декабря 2025" in t:
        return "25-30.12.2025"
    if "27 декабря 2025" in t or "26 декабря 2025" in t:
        return "27.12.2025"
    if "28 декабря 2025" in t:
        return "28.12.2025"
    if "2 января 2026" in t:
        return "02.01.2026"
    if "3 января 2026" in t:
        return "03.01.2026"
    if "4 января 2026" in t:
        return "04.01.2026"
    if "6 января 2026" in t:
        return "06.01.2026"
    return "другое"


def event_format_tag(format_str: str) -> str:
    f = format_str.lower()
    if "шоу" in f:
        return "шоу"
    if "мюзикл" in f or "спектакль" in f:
        return "театр"
    if "концерт" in f or "трибьют" in f:
        return "концерт"
    if "экскурс" in f or "погружение" in f:
        return "экскурсия"
    if "цирк" in f:
        return "цирк"
    return "прочее"


def filter_events(date_choice: str, price_choice: str, fmt_choice: str) -> list[dict]:
    out = []
    for e in EVENTS.values():
        d = event_date_key(e["time"])
        p = normalize_price_to_int(e["price"])
        is_free = (p == 0)
        tag = event_format_tag(e["format"])

        if date_choice != "Любая дата" and date_choice != d:
            continue
        if price_choice == "Только бесплатно" and not is_free:
            continue
        if price_choice == "Только платно" and is_free:
            continue
        if fmt_choice != "Любой формат" and fmt_choice != tag:
            continue

        out.append(e)
    return out


# =========================
# FSM STATES
# =========================
class FilterForm(StatesGroup):
    date = State()
    price = State()
    fmt = State()


# =========================
# KEYBOARDS
# =========================
kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Что такое ночь музеев?")],
        [
            KeyboardButton(text="Расскажи про все мероприятия."),
            KeyboardButton(text="Хочу посмотреть фильтры."),
        ],
        [KeyboardButton(text="Составь мое расписание")],
        [KeyboardButton(text="События в Тюмени")],
        [KeyboardButton(text="Отзывы (ссылка)")],
    ],
    resize_keyboard=True,
)

kb_about = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True,
)

kb_back_to_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 В меню")]],
    resize_keyboard=True,
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
    resize_keyboard=True,
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
    resize_keyboard=True,
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
    resize_keyboard=True,
)

kb_plan_actions = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Концерт в Конторе")],
        [KeyboardButton(text="Квест в Словцова")],
        [KeyboardButton(text="Выставка в Колокольникова")],
        [KeyboardButton(text="Далее")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True,
)

kb_filters_date = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="23.12.2025"), KeyboardButton(text="24.12.2025")],
        [KeyboardButton(text="27.12.2025"), KeyboardButton(text="28.12.2025")],
        [KeyboardButton(text="25-30.12.2025")],
        [KeyboardButton(text="02.01.2026"), KeyboardButton(text="03.01.2026")],
        [KeyboardButton(text="04.01.2026"), KeyboardButton(text="06.01.2026")],
        [KeyboardButton(text="Любая дата")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True,
)

kb_filters_price = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Только бесплатно"), KeyboardButton(text="Только платно")],
        [KeyboardButton(text="Любая цена")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True,
)

kb_filters_format = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="шоу"), KeyboardButton(text="театр")],
        [KeyboardButton(text="концерт"), KeyboardButton(text="экскурсия")],
        [KeyboardButton(text="цирк"), KeyboardButton(text="прочее")],
        [KeyboardButton(text="Любой формат")],
        [KeyboardButton(text="🔙 В меню")],
    ],
    resize_keyboard=True,
)

kb_events_tyumen = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Открыть афишу Тюмени", url=EVENTS_TYUMEN_LINK)]]
)

kb_feedback_link = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Оставить отзыв", url=FEEDBACK_LINK)]]
)

# =========================
# OPTIONS
# =========================
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

# =========================
# HANDLERS
# =========================
@dp.message(CommandStart())
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
        reply_markup=kb_about,
    )


@dp.message(lambda m: m.text == "🔙 Назад")
async def back_from_about(message: types.Message):
    await message.answer("Ок, возвращаемся в главное меню. Чем могу помочь?", reply_markup=kb_main)


@dp.message(lambda m: m.text == "🔙 В меню")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ок, возвращаемся в главное меню.", reply_markup=kb_main)


# ---- LINKS ----
@dp.message(lambda m: m.text == "События в Тюмени")
async def tyumen_events_link(message: types.Message):
    await message.answer(
        "Вот актуальная афиша событий в Тюмени (откроется в браузере):",
        reply_markup=kb_events_tyumen,
    )


@dp.message(lambda m: m.text == "Отзывы (ссылка)")
async def feedback_link(message: types.Message):
    await message.answer("Оставить отзыв можно по ссылке:", reply_markup=kb_feedback_link)


# ---- QUIZ (расписание) ----
@dp.message(lambda m: m.text == "Составь мое расписание")
async def start_quiz(message: types.Message):
    user_id = message.from_user.id
    answers[user_id] = {"company": None, "age": None, "activities": []}
    await message.answer("Хорошо, давай подберём тебе маршрут. В какой компании ты идёшь?", reply_markup=kb_company)


@dp.message(lambda m: m.text in COMPANY_OPTIONS)
async def ask_age(message: types.Message):
    user_id = message.from_user.id
    answers.setdefault(user_id, {"company": None, "age": None, "activities": []})
    answers[user_id]["company"] = message.text
    await message.answer("Сколько лет тебе (и тем, кто пойдёт с тобой, если вы идёте вместе)?", reply_markup=kb_age)


@dp.message(lambda m: m.text in AGE_OPTIONS)
async def ask_activity(message: types.Message):
    user_id = message.from_user.id
    answers.setdefault(user_id, {"company": None, "age": None, "activities": []})
    answers[user_id]["age"] = message.text
    await message.answer(
        "Что ты хочешь делать в Ночь музеев? (можно выбрать несколько пунктов по очереди).\n"
        "Когда закончишь выбор, напиши 'Готово'.",
        reply_markup=kb_activity,
    )


@dp.message(lambda m: m.text in ACTIVITY_OPTIONS)
async def collect_activities(message: types.Message):
    user_id = message.from_user.id
    answers.setdefault(user_id, {"company": None, "age": None, "activities": []})
    if message.text not in answers[user_id]["activities"]:
        answers[user_id]["activities"].append(message.text)
    await message.answer(f"Ок, добавляю: {message.text}. Можешь выбрать ещё или написать 'Готово'.")


@dp.message(lambda m: (m.text or "").strip().lower() == "готово")
async def finish_quiz(message: types.Message):
    user_id = message.from_user.id
    data = answers.get(user_id)

    if not data:
        await message.answer("Пока нет данных. Нажми «Составь мое расписание» и пройди мини-опрос.", reply_markup=kb_main)
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
        reply_markup=kb_main,
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

    # если файлов нет на сервере — можно удалить эти 2 строки
    if os.path.exists("map.jpg"):
        await message.answer_photo(FSInputFile("map.jpg"))


@dp.message(lambda m: m.text == "Концерт в Конторе")
async def action_kontora(message: types.Message):
    await message.answer("Концерт в Конторе Пароходства: приходи чуть раньше, чтобы занять места.")


@dp.message(lambda m: m.text == "Квест в Словцова")
async def action_slovtsov(message: types.Message):
    await message.answer("Квест в музее им. Словцова: будь на месте за 10 минут, чтобы зарегистрироваться.")


@dp.message(lambda m: m.text == "Выставка в Колокольникова")
async def action_kolok(message: types.Message):
    await message.answer("Выставка в музее им. Колокольникова: можно приходить в любое время в указанном интервале.")


@dp.message(lambda m: m.text == "Далее")
async def after_route(message: types.Message):
    await message.answer(
        "Если захочешь сделать паузу после маршрута, на этой карте отмечены дополнительные точки рядом.\n\n"
        "Подробнее о точке на карте: https://go.2gis.com/4WwnM"
    )
    if os.path.exists("map_cafe.jpg"):
        await message.answer_photo(FSInputFile("map_cafe.jpg"))


# ---- ALL EVENTS (старый текст) ----
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


# ---- FILTERS FSM ----
@dp.message(lambda m: m.text == "Хочу посмотреть фильтры.")
async def filters_start(message: types.Message, state: FSMContext):
    await state.set_state(FilterForm.date)
    await message.answer("Выбери дату:", reply_markup=kb_filters_date)


@dp.message(FilterForm.date)
async def filters_date(message: types.Message, state: FSMContext):
    if message.text == "🔙 В меню":
        await state.clear()
        await message.answer("Ок, главное меню.", reply_markup=kb_main)
        return

    await state.update_data(date=message.text)
    await state.set_state(FilterForm.price)
    await message.answer("Цена:", reply_markup=kb_filters_price)


@dp.message(FilterForm.price)
async def filters_price(message: types.Message, state: FSMContext):
    if message.text == "🔙 В меню":
        await state.clear()
        await message.answer("Ок, главное меню.", reply_markup=kb_main)
        return

    await state.update_data(price=message.text)
    await state.set_state(FilterForm.fmt)
    await message.answer("Формат:", reply_markup=kb_filters_format)


@dp.message(FilterForm.fmt)
async def filters_format(message: types.Message, state: FSMContext):
    if message.text == "🔙 В меню":
        await state.clear()
        await message.answer("Ок, главное меню.", reply_markup=kb_main)
        return

    await state.update_data(fmt=message.text)
    data = await state.get_data()
    await state.clear()

    date_choice = data.get("date", "Любая дата")
    price_choice = data.get("price", "Любая цена")
    fmt_choice = data.get("fmt", "Любой формат")

    found = filter_events(date_choice, price_choice, fmt_choice)

    if not found:
        await message.answer("По этим фильтрам ничего не нашлось.", reply_markup=kb_main)
        return

    lines = []
    for e in found[:10]:
        lines.append(
            f"• {e['title']}\n"
            f"  Время: {e['time']}\n"
            f"  Адрес: {e['address']}\n"
            f"  Цена: {e['price']}"
        )

    await message.answer("Нашла варианты:\n\n" + "\n\n".join(lines), reply_markup=kb_main)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())