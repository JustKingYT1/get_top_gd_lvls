# search.py
import json
import re
import settings
import requests
import os

class LevelSearch:
    """Класс для поиска уровней по имени, рангу и длительности."""

    def __init__(self, data):
        self.data = self._process_data(data)

    def _process_data(self, raw_data):
        """Обрабатывает сырые данные, конвертируя 'length' в секунды."""
        processed = []
        for level in raw_data:
            length_str = level.get("length")
            if length_str and ':' in length_str:
                try:
                    minutes, seconds = map(int, length_str.split(':'))
                    level['duration_seconds'] = minutes * 60 + seconds
                except (ValueError, TypeError):
                    level['duration_seconds'] = 0 # Если данные некорректны
            else:
                level['duration_seconds'] = 0
            processed.append(level)
        return processed

    @classmethod
    def from_file(cls, path=settings.OUTPUT_FILE):
        """Загружает данные из локального JSON файла."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ Локально загружено {len(data)} уровней из {path}")
            return cls(data)
        except FileNotFoundError:
            print(f"❌ Локальный файл не найден по пути: {path}")
            return cls([])

    @classmethod
    def from_url(cls, url, local_file_path):
        """
        Загружает данные по URL из GitHub Raw и сохраняет их в локальный файл,
        перезаписывая его, если он существует.
        """
        try:
            # Шаг 1: Загрузка данных по URL
            response = requests.get(url)
            response.raise_for_status()  # Проверка на ошибки HTTP (404, 500..)
            data = response.json()
            print(f"✅ Успешно загружено {len(data)} записей по URL.")

            # Шаг 2: Сохранение данных в локальный файл с перезаписью
            # Открываем файл в режиме 'w' (write), что автоматически
            # создаст файл, если его нет, или перезапишет, если он существует.
            with open(local_file_path, 'w', encoding='utf-8') as f:
                # Используем json.dump для красивой записи JSON в файл
                # ensure_ascii=False для корректного отображения не-ASCII символов
                # indent=4 для форматирования с отступами
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ Данные успешно сохранены в файл: {os.path.abspath(local_file_path)}")

            return cls(data)
        except requests.RequestException as e:
            print(f"❌ Не удалось загрузить данные по URL: {e}")
            return cls([])
        except IOError as e:
            print(f"❌ Ошибка при записи в файл: {e}")
            return cls([])
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка декодирования JSON: {e}")
            return cls([])

    def _parse_user_duration(self, query: str) -> int:
        """Парсит запрос пользователя (например, '2m30s') в секунды."""
        total_seconds = 0
        # Ищем минуты (e.g., 2m, 5min)
        minutes_match = re.search(r'(\d+)\s*m', query, re.IGNORECASE)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        
        # Ищем секунды (e.g., 90s, 30sec)
        seconds_match = re.search(r'(\d+)\s*s', query, re.IGNORECASE)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))

        # Если нет 'm' или 's', считаем что это просто секунды
        if not minutes_match and not seconds_match and query.isdigit():
            total_seconds = int(query)
            
        return total_seconds

    def search_by_name_or_rank(self, query):
        """Поиск по названию или рангу."""
        if query.isdigit():
            rank = int(query)
            return [lvl for lvl in self.data if lvl["rank"] == rank]
        
        query_low = query.lower()
        return [lvl for lvl in self.data if query_low in lvl["name"].lower()]

    def search_by_duration(self, query):
        """Поиск уровней, которые длиннее или равны указанной длительности."""
        required_seconds = self._parse_user_duration(query)
        if required_seconds == 0:
            return []
        
        print(f"Ищем уровни длиннее {required_seconds} секунд...")
        return [lvl for lvl in self.data if lvl['duration_seconds'] >= required_seconds]

    def interactive(self):
        """Запускает интерактивный режим поиска."""
        if not self.data:
            print("Нет данных для поиска. Завершение работы.")
            return

        while True:
            prompt = (
                "\n🔎 Введите запрос для поиска:\n"
                " - Ранг (например, '1')\n"
                " - Часть названия (например, 'slaughterhouse')\n"
                " - Длительность (например, 'len > 2m30s' или 'len > 150s')\n"
                "   (Нажмите Enter для выхода)\n> "
            )
            q = input(prompt).strip()

            if not q:
                break

            results = []
            if q.lower().startswith('len >'):
                duration_query = q[5:].strip()
                results = self.search_by_duration(duration_query)
            else:
                results = self.search_by_name_or_rank(q)
            
            if not results:
                print("❌ Ничего не найдено.")
                continue

            # Сортируем результаты по рангу для наглядности
            results.sort(key=lambda x: x["rank"])

            print(f"\n✨ Найдено результатов: {len(results)}")
            for r in results:
                duration = r['duration_seconds']
                length_str = f"{duration // 60}:{duration % 60:02d}"
                print(f"  #{r['rank']:<4} - {r['name']} (Длительность: {length_str})\n     {r['link']}")