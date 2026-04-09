# 🚀 Quick Start Guide - Модуль "Склад ЗИП"

## ⚡ Быстрое начало работы

### Шаг 1: Убедитесь, что базы данных обновлены
```python
# Backend должен автоматически создать таблицы при старте
# Проверьте что в app.py есть:
Base.metadata.create_all(bind=engine)
```

### Шаг 2: Добавьте компоненты в Store.vue

Откройте `frontend/src/views/Store.vue` и добавьте импорты:

```vue
<script setup>
import InventoryManagement from '../components/store/InventoryManagement.vue'
import InventoryRequestsList from '../components/store/InventoryRequestsList.vue'
</script>

<template>
  <div class="store-container">
    <!-- Новые вкладки -->
    <div class="store-tabs">
      <button @click="currentView = 'inventory'">
        Управление товарами
      </button>
      <button @click="currentView = 'requests'">
        Заявки на пополнение
      </button>
    </div>
    
    <InventoryManagement v-if="currentView === 'inventory'" />
    <InventoryRequestsList v-if="currentView === 'requests'" />
  </div>
</template>

<script>
import { ref } from 'vue'

const currentView = ref('inventory')
</script>
```

### Шаг 3: Добавьте виджет на Dashboard

Откройте `frontend/src/views/Dashboard.vue` и добавьте:

```vue
<script setup>
import InventoryAlerts from '../components/store/InventoryAlerts.vue'
</script>

<template>
  <div class="dashboard">
    <!-- Существующие элементы -->
    
    <!-- Новый виджет для оповещений -->
    <div class="widgets-row">
      <InventoryAlerts />
    </div>
  </div>
</template>
```

### Шаг 4: Добавьте локализацию

В `frontend/src/locales/ru.json` добавьте секцию:

```json
{
  "inventory": {
    "warehouseTitle": "Управление складом ЗИП",
    "alertsTitle": "Оповещения по запасам",
    "requestsTitle": "Заявки на пополнение",
    "addItem": "Добавить товар",
    "checkLowStock": "Проверить при запасы",
    "refresh": "Обновить",
    "totalItems": "Всего товаров",
    "lowStockItems": "Низкий запас",
    "criticalItems": "Критичные",
    "article": "Артикул",
    "name": "Название",
    "nameRus": "Название (РУ)",
    "nameEng": "Название (EN)",
    "currentStock": "Текущее кол-во",
    "minStock": "Мин. запас",
    "available": "Доступно",
    "storage": "Склад",
    "activeRequests": "Активных заявок",
    "actions": "Действия",
    "edit": "Редактировать",
    "delete": "Удалить",
    "cancel": "Отменить",
    "save": "Сохранить",
    "statusNew": "Новая",
    "statusInProcess": "В процессе",
    "statusCompleted": "Выполнена",
    "statusCancelled": "Отменена",
    "reasonManual": "Ручная",
    "reasonAuto": "Автоматическая",
    "quantity": "Кол-во",
    "createdDate": "Создана",
    "createdBy": "Создал",
    "plannedDelivery": "План. доставка",
    "comment": "Комментарий",
    "noItems": "Нет товаров на складе",
    "noRequests": "Нет заявок",
    "noAlerts": "Нет оповещений",
    "unreadAlerts": "Непрочитанных",
    "criticalAlerts": "Критичных",
    "markAllRead": "Прочитать все",
    "itemArticle": "Артикул товара",
    "itemName": "Название товара",
    "viewDetails": "Посмотреть детали",
    "viewRequests": "Просмотр заявок",
    "createRequest": "Создать заявку",
    "editItem": "Редактировать товар",
    "addFirstItem": "Добавить первый товар",
    "enterQuantity": "Введите количество",
    "requestCreated": "Заявка создана успешно",
    "requestError": "Ошибка при создании заявки",
    "confirmDelete": "Вы уверены что хотите удалить этот товар?",
    "confirmCancel": "Вы уверены что хотите отменить заявку?",
    "itemInfo": "Информация о товаре",
    "requestInfo": "Информация о заявке",
    "relatedRepair": "Связанный ремонт",
    "repairDetailId": "ID этапа ремонта",
    "dateSaved": "Дата сохранена",
    "checkCompleted": "Проверка завершена",
    "saveError": "Ошибка при сохранении товара",
    "loadError": "Ошибка при загрузке данных",
    "updateError": "Ошибка при обновлении",
    "deleteError": "Ошибка при удалении",
    "requestsFor": "Заявки для",
    "noRequestsForItem": "Нет заявок для этого товара",
    "justNow": "только что",
    "viewAllRequests": "Все заявки",
    "pdfUrl": "Ссылка на документацию",
    "allStatuses": "Все статусы"
  },
  "common": {
    "cancel": "Отмена",
    "save": "Сохранить"
  },
  "time": {
    "justNow": "только что"
  }
}
```

### Шаг 5: Инициализируйте начальные данные (опционально)

Если у вас нет товаров на складе, добавьте их через интерфейс:

1. Откройте вкладку "Управление товарами"
2. Нажмите кнопку "➕ Добавить товар"
3. Заполните форму:
   - **Артикул**: (уникальный, например "ZIP-001")
   - **Название РУ**: (например "Конденсатор")
   - **Текущее кол-во**: (число)
   - **Мин. запас**: (пороговое значение)
   - **Склад**: (название места хранения)

## 📱 Типичные операции

### Создать заявку на пополнение

**Способ 1: Через таблицу товаров**
1. Найдите товар в InventoryManagement
2. Нажмите кнопку "➕" в графе "Действия"
3. Введите количество
4. Заявка создана!

**Способ 2: Вручную (InventoryRequestsList)**
1. Перейдите на вкладку "Заявки на пополнение"
2. Нажмите кнопку "Создать заявку"
3. Выберите товар, количество, дату доставки

### Отметить заявку как выполненную

1. В таблице InventoryRequestsList выберите заявку
2. В столбце "Статус" выберите из dropdown:
   - "в_процессе" → товар подготавливается
   - "выполнена" → товар выдан, запас автоматически уменьшится
   
## 🔍 где найти данные

| Компонент | Файл | Функция |
|-----------|------|---------|
| Управление товарами | `InventoryManagement.vue` | Таблица товаров, добавление, редактирование |
| Заявки на пополнение | `InventoryRequestsList.vue` | Управление заявками, смена статусов |
| Оповещения (Dashboard) | `InventoryAlerts.vue` | Виджет с последними уведомлениями |
| API клиент | `api.js` | `inventoryApi`, `inventoryRequestApi`, `inventoryAlertApi` |
| Модели БД | `models.py` | `InventoryItem`, `InventoryRequest`, `InventoryAlert` |

## 🆘 Частые вопросы

**Q: Где хранятся товары на складе?**  
A: В таблице БД `inventory_items`. Изначально таблица пуста, требуется добавить через интерфейс.

**Q: Что происходит при создании заявки?**  
A: В БД создаётся запись в `inventory_requests`, создаётся оповещение в `inventory_alerts`, видно на Dashboard.

**Q: Как работает автоматическое уменьшение запаса?**  
A: Когда заявка переходит на статус "выполнена", система уменьшает `current_count` товара на величину `requested_quantity`.

**Q: Что такое "Доступно"?**  
A: Это `current_count` минус количество товара в активных заявках (статусы "новая" и "в_процессе").

**Q: Могу ли я автоматизировать проверку запасов?**  
A: Да! Нажмите кнопку "⚠️ Проверить запасы" в InventoryManagement, система проверит товары с низким запасом и создаст заявки автоматически.

## 📊 Рекомендуемая структура хранения

```
Склад 1 (Основной):
  - ZIP-001: Конденсатор (10 шт, мин. 5)
  - ZIP-002: Резистор (50 шт, мин. 20)
  - ZIP-003: Диод (100 шт, мин. 50)

Склад 2 (Запасной):
  - ZIP-004: Микросхема (5 шт, мин. 2)
```

## 🐛 Отладка

Если что-то не работает, проверьте:

1. **Backend работает?**
   ```
   curl http://localhost:8000/api/inventory
   ```
   Должен вернуть пустой массив `[]` или товары JSON

2. **Frontend видит API?**
   Откройте DevTools (F12) → NetworkConsole, проверьте запросы к `/api/inventory`

3. **БД создана?**
   Backend должен создать таблицы автоматически при первом запуске.

4. **Импорты верны?**
   Проверьте что все компоненты импортированы правильно в Store.vue и Dashboard.vue

## ✅ Контрольный список интеграции

- [ ] Backend запущен и базы данных созданы
- [ ] Добавлены импорты InventoryManagement и InventoryRequestsList в Store.vue
- [ ] Добавлен InventoryAlerts на Dashboard
- [ ] Добавлены ключи локализации в ru.json
- [ ] Приложение перезагружено (F5 в браузере)
- [ ] Можно добавить товар через InventoryManagement
- [ ] Видны оповещения на Dashboard
- [ ] Можно создать заявку и обновить её статус

## 📞 Помощь и поддержка

Все API endpoints полностью документированы в коде с docstring'ами.

**При возникновении проблем:**
1. Проверьте консоль браузера (DevTools)
2. Проверьте логи backend'а
3. Убедитесь что все файлы скопированы и не имеют синтаксических ошибок

---

**Готово к использованию! Успехов с дипломной работой! 🎓**
