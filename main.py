import asyncio
from bot import DemonlistBot

def main():
    print("🚀 Запускаем Telegram-бота Demonlist...")
    bot = DemonlistBot()
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()