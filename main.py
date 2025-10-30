# main.py
from scraper.scraper import DemonlistScraper
from search import LevelSearch
import os, datetime
import settings

def is_file_from_today(path):
    """Проверяет, соответствует ли JSON сегодняшнему дню."""
    if not os.path.exists(path):
        return False
    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return mod_time.date() == datetime.date.today()

def main():
    if not is_file_from_today(settings.OUTPUT_FILE):
        print("🆕 Сегодняшнего файла нет, создаём новый...")
        scraper = DemonlistScraper()
        data = scraper.run()
    else:
        print("📂 Используем существующий файл за сегодня.")
        searcher = LevelSearch.from_file()
        data = searcher.data

    LevelSearch(data).interactive()
    print("👋 Завершено.")

if __name__ == "__main__":
    main()
