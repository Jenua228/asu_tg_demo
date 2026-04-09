"""
Скрипт миграции базы данных - добавляет новые поля без потери данных.
Запускать: python migrate.py
"""
import sqlite3
import os

DB_PATH = "app.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("База данных не найдена. Будет создана при запуске main.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Список новых полей для добавления в таблицу report_records
    # Формат: (имя_столбца, тип_данных, значение_по_умолчанию)
    new_columns_reports = [
        ("tcr", "VARCHAR(100)", "''"),
        ("planned_start_date", "VARCHAR(50)", "''"),
        ("comments", "TEXT", "''"),
    ]
    
    # Получаем существующие столбцы таблицы report_records
    cursor.execute("PRAGMA table_info(report_records)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Добавляем недостающие столбцы
    for col_name, col_type, default_value in new_columns_reports:
        if col_name not in existing_columns:
            try:
                sql = f"ALTER TABLE report_records ADD COLUMN {col_name} {col_type} DEFAULT {default_value}"
                cursor.execute(sql)
                print(f"✅ Добавлен столбец: {col_name}")
            except Exception as e:
                print(f"⚠️  Столбец {col_name} уже существует или ошибка: {e}")
        else:
            print(f"ℹ️  Столбец {col_name} уже существует")
    
    conn.commit()
    conn.close()
    print("\n✅ Миграция завершена!")

if __name__ == "__main__":
    migrate()