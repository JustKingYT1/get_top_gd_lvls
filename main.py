import asyncio
from bot import DemonlistBotSync

def main():
    print("🚀 Запускаем Telegram-бота Demonlist...")
    bot = DemonlistBotSync()
    bot.run()

if __name__ == "__main__":
    main()