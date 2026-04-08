import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Проверяем, существует ли уже колонка
cursor.execute("PRAGMA table_info(repair_details)")
columns = [col[1] for col in cursor.fetchall()]

if 'comment' not in columns:
    cursor.execute("ALTER TABLE repair_details ADD COLUMN comment TEXT")
    print("Колонка 'comment' добавлена успешно!")
else:
    print("Колонка 'comment' уже существует")

conn.commit()
conn.close()