import requests
import os
from datetime import datetime
from settings import GITHUB_RAW_URL, LOCAL_DATA_PATH, BOT_TOKEN, ADMIN_ID

def send_telegram_message(text):
    """Отправляет уведомление администратору через Telegram"""
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": ADMIN_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(api_url, data=data, timeout=10)
    except Exception as e:
        print(f"❌ Не удалось отправить уведомление в Telegram: {e}")

def update_json():
    log_msg = f"🚀 [{datetime.now()}] Начинаем обновление demonlist.json...\n"
    print(log_msg.strip())
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=30)
        r.raise_for_status()

        os.makedirs(os.path.dirname(LOCAL_DATA_PATH), exist_ok=True)
        with open(LOCAL_DATA_PATH, "w", encoding="utf-8") as f:
            f.write(r.text)

        success_msg = f"✅ Файл успешно обновлён: {LOCAL_DATA_PATH}"
        print(success_msg)
        log_msg += success_msg
        send_telegram_message(f"✅ Demonlist обновлён успешно!\n{datetime.now()}")

    except requests.exceptions.RequestException as e:
        err_msg = f"❌ Ошибка сети при обновлении: {e}"
        print(err_msg)
        log_msg += err_msg
        send_telegram_message(f"❌ Ошибка при обновлении Demonlist!\n{e}")
    except Exception as e:
        err_msg = f"❌ Другая ошибка при обновлении: {e}"
        print(err_msg)
        log_msg += err_msg
        send_telegram_message(f"❌ Другая ошибка при обновлении Demonlist!\n{e}")

    # Лог
    log_file = os.path.join(os.path.dirname(LOCAL_DATA_PATH), "update.log")
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(log_msg + "\n")

if __name__ == "__main__":
    update_json()
