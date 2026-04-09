from database import SessionLocal, engine
import models

# Создаём сессию
db = SessionLocal()

# Обновляем все записи где unit_measurement пусто
items = db.query(models.InventoryItem).all()
for item in items:
    if not item.unit_measurement or item.unit_measurement.strip() == '':
        item.unit_measurement = 'шт.'

db.commit()
print(f"✅ Обновлено {len(items)} записей")
db.close()