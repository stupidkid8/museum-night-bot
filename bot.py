import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("8441700443:AAEuMOkI5zeIC015y8hxng4i5rLqWAPWbKU")

# Куда слать отзывы админу (если не нужно — оставь None)
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # например "123456789"
ADMIN_CHAT_ID = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID and ADMIN_CHAT_ID.isdigit() else None

# Ссылка/контакт для отзывов (Google Form / сайт / etc.)
FEEDBACK_LINK = os.getenv("FEEDBACK_LINK", "https://example.com/feedback")


# =========================
# DATA: EVENTS (15 шт)
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

EVENT_TITLES = list(EVENTS.keys())


# =========================
# HELPERS: FILTERS
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
    if "27 декабря 2025" in t:
        return "27.12.2025"
    if "26 декабря 2025" in t:
        return "27.12.2025"
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


def filter_events(date_choice: str, price_choice: str, fmt_choice: str) -> list[str]:
    out = []
    for key, e in EVENTS.items():
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

        out.append(key)

    return out


def kb_from_event_keys(keys: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=k)] for k in keys] + [[KeyboardButton(text="🔙 В меню")]],
        resize_keyboard=True,
    )


# =========================
# KEYBOARDS
# =========================
kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Что такое ночь музеев?")],
        [KeyboardButton(text="Все мероприятия")],
        [KeyboardButton(text="Хочу посмотреть фильтры.")],
        [KeyboardButton(text="Составь мое расписание")],
        [KeyboardButton(text="Оставить отзыв")],
    ],
    resize_keyboard=True,
)

kb_all_events = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=title)] for title in EVENT_TITLES]
    + [[KeyboardButton(text="🔙 В меню")]],
    resize_keyboard=True,
)

kb_back_to_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 В меню")]],
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


# =========================
# FSM
# =========================
class FeedbackForm(StatesGroup):
    waiting_text = State()


class FilterForm(StatesGroup):
    date = State()
    price = State()
    fmt = State()


# =========================
# HANDLERS
# =========================
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выбирай пункт в меню.", reply_markup=kb_main)


async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню.", reply_markup=kb_main)


async def about(message: types.Message):
    await message.answer(
        "«Ночь музеев» — городская культурная акция: площадки делают спецпрограмму "
        "(экскурсии, квесты, концерты, шоу).",
        reply_markup=kb_main,
    )


async def all_events(message: types.Message):
    await message.answer("Выбери мероприятие — покажу подробности:", reply_markup=kb_all_events)


async def show_event_details(message: types.Message):
    e = EVENTS.get(message.text)
    if not e:
        return

    text = (
        f"<b>{e['title']}</b>\n"
        f"Время: {e['time']}\n"
        f"Адрес: {e['address']}\n"
        f"Формат: {e['format']}\n"
        f"Цена: {e['price']}"
    )

    kb_event_nav = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Все мероприятия")],
            [KeyboardButton(text="Хочу посмотреть фильтры.")],
            [KeyboardButton(text="🔙 В меню")],
        ],
        resize_keyboard=True,
    )

    await message.answer(text, parse_mode="HTML", reply_markup=kb_event_nav)


async def build_schedule(message: types.Message):
    picks = [
        "🎄 Открытие главной городской ёлки (27 декабря)",
        "🎅 Резиденция Деда Мороза (Кристалл)",
        "🎻 Concord Orchestra — Штраус (23 декабря)",
    ]
    lines = []
    for k in picks:
        e = EVENTS.get(k)
        if e:
            lines.append(f"• {e['title']} — {e['time']} — {e['address']}")

    await message.answer(
        "Персональное предложение (черновик):\n\n"
        + "\n".join(lines)
        + "\n\nХочешь точнее — напиши: дата, бюджет, с кем идёшь (один/пара/дети), что не любишь.",
        reply_markup=kb_main,
    )


# ---- FILTERS FSM ----
async def filters_start(message: types.Message, state: FSMContext):
    await state.set_state(FilterForm.date)
    await message.answer("Выбери дату:", reply_markup=kb_filters_date)


async def filters_date(message: types.Message, state: FSMContext):
    if message.text == "🔙 В меню":
        await state.clear()
        await message.answer("Главное меню.", reply_markup=kb_main)
        return

    await state.update_data(date=message.text)
    await state.set_state(FilterForm.price)
    await message.answer("Цена:", reply_markup=kb_filters_price)


async def filters_price(message: types.Message, state: FSMContext):
    if message.text == "🔙 В меню":
        await state.clear()
        await message.answer("Главное меню.", reply_markup=kb_main)
        return

    await state.update_data(price=message.text)
    await state.set_state(FilterForm.fmt)
    await message.answer("Формат:", reply_markup=kb_filters_format)


async def filters_format(message: types.Message, state: FSMContext):
    if message.text == "🔙 В меню":
        await state.clear()
        await message.answer("Главное меню.", reply_markup=kb_main)
        return

    await state.update_data(fmt=message.text)
    data = await state.get_data()
    await state.clear()

    date_choice = data.get("date", "Любая дата")
    price_choice = data.get("price", "Любая цена")
    fmt_choice = data.get("fmt", "Любой формат")

    keys = filter_events(date_choice, price_choice, fmt_choice)

    if not keys:
        await message.answer(
            "По этим фильтрам ничего не нашлось. Попробуй другие значения.",
            reply_markup=kb_main,
        )
        return

    await message.answer(
        f"Нашлось: {len(keys)}. Выбирай мероприятие:",
        reply_markup=kb_from_event_keys(keys),
    )


# ---- FEEDBACK FSM ----
async def feedback_start(message: types.Message, state: FSMContext):
    await state.set_state(FeedbackForm.waiting_text)
    await message.answer(
        "Напиши отзыв одним сообщением.\n"
        f"Если удобнее — можно по ссылке: {FEEDBACK_LINK}",
        reply_markup=kb_back_to_menu,
    )


async def feedback_receive(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Отзыв пустой. Напиши текстом, пожалуйста.", reply_markup=kb_back_to_menu)
        return

    user = message.from_user
    meta = f"Отзыв от: {user.full_name} (@{user.username}) id={user.id}" if user else "Отзыв"

    if ADMIN_CHAT_ID:
        try:
            await message.bot.send_message(ADMIN_CHAT_ID, f"{meta}\n\n{text}")
        except Exception:
            pass

    await state.clear()
    await message.answer("Принято. Спасибо!", reply_markup=kb_main)


async def fallback(message: types.Message):
    await message.answer("Не понял. Нажми кнопку в меню.", reply_markup=kb_main)


# =========================
# MAIN
# =========================
async def main():
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_TOKEN_HERE":
        raise RuntimeError("Укажи BOT_TOKEN (env BOT_TOKEN или строкой в коде).")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.register(cmd_start, CommandStart())
    dp.message.register(lambda m, state: back_to_menu(m, state), lambda m: m.text == "🔙 В меню")

    dp.message.register(about, lambda m: m.text == "Что такое ночь музеев?")
    dp.message.register(all_events, lambda m: m.text == "Все мероприятия")
    dp.message.register(filters_start, lambda m: m.text == "Хочу посмотреть фильтры.")
    dp.message.register(build_schedule, lambda m: m.text == "Составь мое расписание")

    dp.message.register(feedback_start, lambda m: m.text == "Оставить отзыв")
    dp.message.register(feedback_receive, FeedbackForm.waiting_text)

    dp.message.register(show_event_details, lambda m: m.text in EVENT_TITLES)

    dp.message.register(filters_date, FilterForm.date)
    dp.message.register(filters_price, FilterForm.price)
    dp.message.register(filters_format, FilterForm.fmt)

    dp.message.register(fallback)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
