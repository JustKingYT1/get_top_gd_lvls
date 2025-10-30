import requests
import time
import os
from search import LevelSearch
from settings import BOT_TOKEN, LOCAL_DATA_PATH
from datetime import datetime

class DemonlistBotSync:
    def __init__(self):
        self.token = BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.searcher = None
        self.offset = None
        self._last_mtime = None  # для отслеживания изменений JSON

    def load_data(self):
        if os.path.exists(LOCAL_DATA_PATH):
            print(f"🔄 [{datetime.now()}] Загружаем данные из локального JSON...")
            self.searcher = LevelSearch.from_file(LOCAL_DATA_PATH)
            print(f"✅ Данные загружены, уровней: {len(self.searcher.data)}")
        else:
            print("⚠️ Локальный файл demonlist.json не найден!")
            self.searcher = LevelSearch([])

    def reload_data(self):
        """Обновляем данные после изменения JSON"""
        self.load_data()

    def check_reload(self):
        """Проверяет, обновился ли JSON, и перезагружает данные"""
        try:
            mtime = os.path.getmtime(LOCAL_DATA_PATH)
            if self._last_mtime is None:
                self._last_mtime = mtime
            elif mtime != self._last_mtime:
                print("🔄 Обнаружено обновление demonlist.json, перезагружаем данные...")
                self.reload_data()
                self._last_mtime = mtime
        except FileNotFoundError:
            pass

    def send_message(self, chat_id, text):
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            requests.post(f"{self.api_url}/sendMessage", data=data, timeout=10)
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение: {e}")

    def handle_message(self, message):
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
        """Главный цикл polling бота с авто-обновлением JSON"""
        self.load_data()
        print("🤖 Бот запущен и ждёт сообщений...")

        while True:
            self.check_reload()  # проверяем, нужно ли обновить данные

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
                time.sleep(5)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)


if __name__ == "__main__":
    bot = DemonlistBotSync()
    bot.run()
