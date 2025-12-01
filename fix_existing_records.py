# fix_existing_records.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("Исправление записей с NULL временем...")

# Устанавливаем текущее время для всех записей с NULL
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
cursor.execute("""
    UPDATE Data_peopleinpublictransport 
    SET time = ? 
    WHERE time IS NULL
""", (current_time,))

print(f"Исправлено записей: {cursor.rowcount}")

# Проверяем результат
cursor.execute("SELECT COUNT(*) FROM Data_peopleinpublictransport WHERE time IS NULL;")
remaining = cursor.fetchone()[0]
print(f"Осталось записей с NULL временем: {remaining}")

conn.commit()
conn.close()
print("Готово!")