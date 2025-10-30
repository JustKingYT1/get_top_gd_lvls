# main.py
from search import LevelSearch
import os
from settings import GITHUB_RAW_URL, LOCAL_DATA_PATH

def main():
    print("🚀 Запускаю приложение для поиска по Demonlist...")
    
    searcher = None

    # 1. Пытаемся загрузить свежие данные с GitHub
    searcher = LevelSearch.from_url(GITHUB_RAW_URL, LOCAL_DATA_PATH)

    # 2. Если не получилось, или если searcher не был создан, используем локальный файл
    if not searcher or not searcher.data:
        print("\n📂 Не удалось загрузить с GitHub, используем локальный файл...")
        if os.path.exists(LOCAL_DATA_PATH):
            searcher = LevelSearch.from_file(LOCAL_DATA_PATH)
        else:
            print(f"❌ Локальный файл {LOCAL_DATA_PATH} не найден. Данных для поиска нет.")
            searcher = LevelSearch([]) # Создаем пустой экземпляр

    # 3. Запускаем интерактивный режим
    searcher.interactive()

    print("\n👋 Завершено.")


if __name__ == "__main__":
    main()