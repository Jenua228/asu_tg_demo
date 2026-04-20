# import sqlite3

# conn = sqlite3.connect('app.db')
# cursor = conn.cursor()

# # Добавляем колонку (как в варианте 1)
# cursor.execute("PRAGMA table_info(inventory_items)")
# if 'imgName' not in [col[1] for col in cursor.fetchall()]:
#     cursor.execute("ALTER TABLE inventory_items ADD COLUMN imgName TEXT")
#     print("Колонка добавлена.")
# else:
#     print("Колонка 'imgName' уже существует.")

# # Получаем все rowid в порядке возрастания (или любом нужном порядке)
# cursor.execute("SELECT rowid FROM inventory_items ORDER BY rowid")
# rows = cursor.fetchall()

# # Здесь вручную прописываете ссылки в том же порядке, что и строки
# # Длина списка должна совпадать с количеством строк
# links = [
#     "Distribution unit ШИБФ.468353.055.jpg",
#     "Industrial computer ТС-1900 “Тензор” ТСВН.466217.002.jpg",
#     "Digital multimeter Truevolt 34461A.jpg",
#     "Analogue signature analyser АСА ВЦТП.411218.014.jpg",
#     "Interface panel DCH.1Э ШИБФ.468354.031.jpg",
#     "Multiadapter 468353.101.jpg",
#     "Exhaust drier-device ШИБФ.066419.007.jpg",
#     "Static voltage meter АТP‑9365.jpg",
#     "Digital heating system НП24-17про.jpg",
#     "Multifunction digital repair soldering station PACE PRC-2000E.jpg",
#     "Ground resistance meter ИС-20 РАПМ.411212.002.jpg",
#     "sadfg.jpg",
#     "133ln.jpg",
#     "Image1.jpg",
#     "LAN cable spool",
#     "a"
#     # ... добавьте столько же ссылок, сколько строк в таблице
# ]

# if len(links) != len(rows):
#     print(f"Ошибка: количество ссылок ({len(links)}) не совпадает с числом строк ({len(rows)})")
# else:
#     for (rowid,), link in zip(rows, links):
#         cursor.execute("UPDATE inventory_items SET imgName = ? WHERE rowid = ?", (link, rowid))
#     conn.commit()
#     print(f"Обновлено {len(rows)} строк.")

# conn.close()


import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Добавляем колонку reserved_count в inventory_items
cursor.execute("PRAGMA table_info(inventory_items)")
if 'reserved_count' not in [col[1] for col in cursor.fetchall()]:
    cursor.execute("ALTER TABLE inventory_items ADD COLUMN reserved_count INTEGER DEFAULT 0")
    print("Колонка 'reserved_count' добавлена.")
else:
    print("Колонка 'reserved_count' уже существует.")

# Заполнить существующие записи значением 0, если нужно
cursor.execute("UPDATE inventory_items SET reserved_count = 0 WHERE reserved_count IS NULL")

conn.commit()
conn.close()
print("Готово.")