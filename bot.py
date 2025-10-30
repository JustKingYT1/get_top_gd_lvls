import requests
import time
from search import LevelSearch
from settings import BOT_TOKEN, GITHUB_RAW_URL, LOCAL_DATA_PATH
import os

class DemonlistBotSync:
    def __init__(self):
        self.token = BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.searcher = None
        self.offset = None  # для getUpdates

    def load_data(self):
        """Загружает данные с GitHub или локально."""
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

    def send_message(self, chat_id, text):
        """Отправка сообщения пользователю."""
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.post(f"{self.api_url}/sendMessage", data=data)

    def handle_message(self, message):
        """Обработка одного сообщения от пользователя."""
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/start"):
            start_text = (
                "👋 Привет! Я бот для поиска уровней из Demonlist.\n\n"
                "📌 Примеры запросов:\n"
                " - <b>1</b> — поиск по рангу\n"
                " - <b>slaughterhouse</b> — поиск по названию\n"
                " - <b>len > 2m30s</b> или <b>len > 150s</b> — поиск по длине"
            )
            self.send_message(chat_id, start_text)
            return

        query = text.strip()
        if not query:
            self.send_message(chat_id, "❌ Пустой запрос.")
            return

        if not self.searcher or not self.searcher.data:
            self.send_message(chat_id, "⚠️ Данные ещё не загружены. Попробуй чуть позже.")
            return

        if query.lower().startswith("len >"):
            results = self.searcher.search_by_duration(query[5:].strip())
        else:
            results = self.searcher.search_by_name_or_rank(query)

        if not results:
            self.send_message(chat_id, "😔 Ничего не найдено.")
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

        text_reply = "\n\n".join(reply_parts)
        if len(results) > 10:
            text_reply += f"\n\n...и ещё {len(results) - 10} результатов."

        self.send_message(chat_id, text_reply)

    def run(self):
        """Главный цикл бота (polling)."""
        self.load_data()
        print("🤖 Бот запущен и ждёт сообщений...")

        while True:
            params = {"timeout": 100, "offset": self.offset}
            try:
                response = requests.get(f"{self.api_url}/getUpdates", params=params, timeout=120)
                updates = response.json().get("result", [])
                for update in updates:
                    self.offset = update["update_id"] + 1
                    if "message" in update:
                        self.handle_message(update["message"])
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Ошибка сети: {e}")
                time.sleep(5)  # пауза перед повтором
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)
