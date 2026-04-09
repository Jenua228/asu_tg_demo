#!/usr/bin/env python
"""
Скрипт для заполнения БД начальными данными товаров на складе
"""
from database import SessionLocal
import models

def seed_inventory():
    """Вставить начальные данные в таблицу InventoryItem"""
    db = SessionLocal()
    try:
        # Проверяем, не заполнена ли уже БД
        existing_count = db.query(models.InventoryItem).count()
        if existing_count > 0:
            print(f"⚠️  БД уже содержит {existing_count} товаров. Скрипт не запустится повторно.")
            print("Если нужно пересоздать данные, очистите таблицу вручную.")
            return
        
        # Начальные данные товаров
        items_data = [
            {'article': '468353.055', 'name_rus': 'Блок распределительный', 'name_eng': 'Distribution unit', 'current_count': 3, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '466217.002', 'name_rus': 'ЭВМ промышленного назначения TC-1900', 'name_eng': 'Industrial computer TC-1900', 'current_count': 5, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '466234', 'name_rus': 'Цифровой мультиметр Truevolt 34461A', 'name_eng': 'Digital multimeter Truevolt 34461', 'current_count': 12, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': '/doc/ЕФ3.035.074.pdf'},
            {'article': '411218.014', 'name_rus': 'Аналоговый сигнатурный анализатор АСА', 'name_eng': 'Analogue signature analyser ACA', 'current_count': 8, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': '/doc/ЕФ3.035.074 ПЭ3.pdf'},
            {'article': '468354.031', 'name_rus': 'Панель сопряжения Ц.1Э', 'name_eng': 'Interface panel DCH', 'current_count': 7, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '468353.101', 'name_rus': 'Мультиадаптер', 'name_eng': 'Multiadapter', 'current_count': 9, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '066419.007', 'name_rus': 'Устройство сушильно‑вытяжное', 'name_eng': 'Exhaust drier-device', 'current_count': 4, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': '/doc/test2.pdf'},
            {'article': '', 'name_rus': 'Измеритель статического напряжения АТР‑9365', 'name_eng': 'Static voltage meter АТP-9365', 'current_count': 5, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '', 'name_rus': 'Цифровая система пайки', 'name_eng': 'Digital soldering system', 'current_count': 9, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '8007-0133', 'name_rus': 'Многофункциональный цифровой паяльно-ремонтный центр PACE PRC-2000E', 'name_eng': 'Multifunction digital repair soldering station PACE PRC-2000E', 'current_count': 7, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '', 'name_rus': 'Аппарат телефонный «ТА-88»', 'name_eng': 'Telephone set "ТА-88"', 'current_count': 5, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '411212.002', 'name_rus': 'Измеритель сопротивления заземления ИС-20', 'name_eng': 'Ground resistance meter IC-20', 'current_count': 6, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '066419.012', 'name_rus': 'Субблок Н6.17.06.08', 'name_eng': 'Subblock N6.17.06.08', 'current_count': 2, 'min_stock': 1, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': '/doc/Н6.17.06.08-PRD.pdf'},
            {'article': '133LN1', 'name_rus': 'Плата 133ЛН1', 'name_eng': '133ln1', 'current_count': 3, 'min_stock': 6, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': '/doc/ЕФ3.035.074 СБ.PDF'},
            {'article': '533TL2', 'name_rus': '533ТЛ2 элемент', 'name_eng': '533TL2 element', 'current_count': 1, 'min_stock': 2, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
            {'article': '687431.003', 'name_rus': 'Катушка с кабелем ЛВС', 'name_eng': 'LAN cable spool', 'current_count': 9, 'min_stock': 3, 'storage_name': 'Склад ЗИП', 'comment': '', 'pdf_url': ''},
        ]
        
        # Вставляем товары
        for item_data in items_data:
            # Пропускаем товары без артикула (если нужно)
            if not item_data.get('article'):
                item_data['article'] = f"NO-ARTICLE-{item_data['name_rus'][:10]}"
            
            item = models.InventoryItem(
                article=item_data['article'],
                name_rus=item_data['name_rus'],
                name_eng=item_data['name_eng'],
                current_count=item_data['current_count'],
                min_stock=item_data['min_stock'],
                storage_name=item_data['storage_name'],
                comment=item_data['comment'],
                pdf_url=item_data['pdf_url']
            )
            db.add(item)
        
        db.commit()
        print(f"✅ Успешно добавлено {len(items_data)} товаров на склад")
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении БД: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    seed_inventory()
