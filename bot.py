# bot.py
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from search import LevelSearch
from settings import BOT_TOKEN, GITHUB_RAW_URL, LOCAL_DATA_PATH
import os
import aiogram

class DemonlistBot:
    def __init__(self):
        self.bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        self.dp = Dispatcher()
        self.searcher = None

        # Регистрируем хэндлеры
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.handle_query)

    async def load_data(self):
        """Загружает данные с GitHub (или локально, если GitHub недоступен)."""
        print("🚀 Загружаем данные с GitHub...")
        self.searcher = LevelSearch.from_url(GITHUB_RAW_URL, LOCAL_DATA_PATH)
        if not self.searcher.data:
            print("⚠️ Не удалось загрузить с GitHub, пробуем локально...")
            if os.path.exists(LOCAL_DATA_PATH):
                self.searcher = LevelSearch.from_file(LOCAL_DATA_PATH)
            else:
                print("❌ Нет ни локальных, ни сетевых данных!")
                self.searcher = LevelSearch([])
        print(f"✅ Загружено уровней: {len(self.searcher.data)}")

    async def start_command(self, message: types.Message):
        """Обработка команды /start"""
        text = (
            "👋 Привет! Я бот для поиска уровней из Demonlist.\n\n"
            "📌 Примеры запросов:\n"
            " - <b>1</b> — поиск по рангу\n"
            " - <b>slaughterhouse</b> — поиск по названию\n"
            " - <b>len > 2m30s</b> или <b>len > 150s</b> — поиск по длине"
        )
        await message.answer(text)

    async def handle_query(self, message: types.Message):
        """Обрабатывает обычный текст пользователя (поисковый запрос)."""
        query = message.text.strip()
        if not query:
            await message.answer("❌ Пустой запрос.")
            return

        if not self.searcher or not self.searcher.data:
            await message.answer("⚠️ Данные ещё не загружены. Попробуй чуть позже.")
            return

        if query.lower().startswith("len >"):
            results = self.searcher.search_by_duration(query[5:].strip())
        else:
            results = self.searcher.search_by_name_or_rank(query)

        if not results:
            await message.answer("😔 Ничего не найдено.")
            return

        results = sorted(results, key=lambda x: x["rank"])
        reply_parts = []
        for r in results[:10]:
            duration = r["duration_seconds"]
            length_str = f"{duration // 60}:{duration % 60:02d}"
            reply_parts.append(
                f"#{r['rank']} — <b>{r['name']}</b>\n"
                f"🕒 {length_str}\n"
                f"🔗 <a href='{r['link']}'>Ссылка</a>"
            )

        text = "\n\n".join(reply_parts)
        if len(results) > 10:
            text += f"\n\n...и ещё {len(results) - 10} результатов."

        await message.answer(text)

    async def run(self):
        """Запускает бота."""
        await self.load_data()
        print("🤖 Бот запущен и ждёт сообщений...")
        await self.dp.start_polling(self.bot)
