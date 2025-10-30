# search.py
import json
import settings

class LevelSearch:
    """Класс для поиска уровней по имени или рангу."""

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_file(cls, path=settings.OUTPUT_FILE):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ Загружено {len(data)} уровней из {path}")
            return cls(data)
        except FileNotFoundError:
            print("❌ Файл данных не найден.")
            return cls([])

    def search(self, query):
        if query.isdigit():
            rank = int(query)
            return [d for d in self.data if d["rank"] == rank]
        query_low = query.lower()
        return [d for d in self.data if query_low in d["name"].lower()]

    def interactive(self):
        while True:
            q = input("\n🔎 Введи ранг или часть названия (Enter — выход): ").strip()
            if not q:
                break
            results = self.search(q)
            if not results:
                print("❌ Ничего не найдено.")
                continue
            for r in results:
                print(f"#{r['rank']} — {r['name']}\n  {r['link']}")
