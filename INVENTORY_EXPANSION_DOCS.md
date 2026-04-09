# 📦 Расширение модуля "Склад ЗИП" - Подробная документация

## 🎯 Цель проекта
Расширить модуль управления запасами (ЗИП) и связать его с системой планирования работ, чтобы процесс ремонта был неразрывно связан с управлением запасами.

## 📋 Реализованные компоненты

### BACKEND

#### 1. Новые модели базы данных (`backend/models.py`)

**InventoryItem** - Товар на складе
```python
- id: Уникальный идентификатор
- article: Артикул (уникальный)
- name_rus: Название на русском
- name_eng: Название на английском
- current_count: Текущее количество на складе
- min_stock: Минимально допустимое количество
- storage_name: Название места хранения
- comment: Комментарий
- pdf_url: Ссылка на техническую документацию
- created_at, updated_at: Временные метки
```

**InventoryRequest** - Заявка на пополнение
```python
- id: Уникальный идентификатор
- inventory_item_id: Ссылка на товар
- requested_quantity: Запрашиваемое количество
- reason: Тип заявки ('manual' или 'auto')
- status: Статус заявки ('новая', 'в_процессе', 'выполнена', 'отменена')
- related_repair_detail_id: Связь с этапом ремонта (опционально)
- related_report_id: Связь с записью отчёта (опционально)
- created_by: Кто создал заявку
- notification_sent: Отправлена ли уведомление
- planned_delivery_date: Планируемая дата доставки
- actual_delivery_date: Фактическая дата выдачи
- created_at, updated_at: Временные метки
```

**InventoryAlert** - Уведомление/оповещение
```python
- id: Уникальный идентификатор
- inventory_request_id: Ссылка на заявку
- alert_type: Тип ('info', 'warning', 'critical', 'success')
- event_type: Тип события ('new_request', 'auto_request_created', 'request_completed', 'low_stock')
- message: Текст оповещения
- is_read: Статус прочтения
- created_at: Время создания
```

#### 2. API Endpoints

**Управление товарами на складе:**
```
GET    /api/inventory              - Получить все товары
GET    /api/inventory/<id>         - Получить конкретный товар
POST   /api/inventory              - Добавить новый товар
PUT    /api/inventory/<id>         - Обновить товар
DELETE /api/inventory/<id>         - Удалить товар
POST   /api/inventory/check-low-stock - Проверка минимальных запасов и авто-создание заявок
GET    /api/inventory/stats/overview  - Получить статистику
```

**Управление заявками:**
```
GET    /api/inventory-requests              - Получить все заявки
GET    /api/inventory-requests?status=новая - Получить заявки по статусу
GET    /api/inventory-requests/<id>         - Получить конкретную заявку
POST   /api/inventory-requests              - Создать новую заявку
PUT    /api/inventory-requests/<id>         - Обновить статус заявки
DELETE /api/inventory-requests/<id>         - Отменить заявку
```

**Управление оповещениями:**
```
GET    /api/inventory-alerts                     - Получить все оповещения
GET    /api/inventory-alerts?unread=true         - Получить непрочитанные
GET    /api/inventory-alerts?limit=10            - Получить последние N
PUT    /api/inventory-alerts/<id>                - Отметить как прочитанное
POST   /api/inventory-alerts/mark-all-read      - Отметить все как прочитанные
DELETE /api/inventory-alerts/<id>                - Удалить оповещение
```

**Важные особенности:**
- При обновлении заявки на статус "выполнена" автоматически уменьшается `current_count` товара
- При создании заявки автоматически создаётся оповещение
- Функция `check-low-stock` автоматически создаёт заявки для товаров с истощённым запасом

### FRONTEND

#### 1. API клиент (`frontend/src/api.js`)

Добавлены 4 основных объекта API:

```javascript
inventoryApi {
  getAll(),
  get(id),
  create(item),
  update(id, item),
  delete(id),
  checkLowStock()
}

inventoryRequestApi {
  getAll(),
  getAllFiltered(status),
  get(id),
  create(request),
  update(id, request),
  delete(id),
  markAsInProcess(id),
  markAsCompleted(id),
  markAsCancelled(id)
}

inventoryAlertApi {
  getAll(),
  getUnread(),
  getAllLimited(limit),
  markAsRead(id),
  markAllAsRead(),
  delete(id)
}

inventoryStatsApi {
  getOverview()
}
```

#### 2. Компонент InventoryManagement.vue

**Расположение:** `frontend/src/components/store/InventoryManagement.vue`

**Функционал:**
- ✅ Таблица всех товаров на складе
- ✅ Статистика (всего товаров, с низким запасом, критичные)
- ✅ Добавление новых товаров (модальное окно с формой)
- ✅ Редактирование товаров (артикул, названия, количество, минимум, склад, комментарий, PDF)
- ✅ Прямое редактирование количества в таблице (inline)
- ✅ Просмотр активных заявок для товара
- ✅ Создание заявки на товар (быстрое создание через диалог)
- ✅ Проверка минимальных запасов и автоматическое создание заявок
- ✅ Удаление товаров
- ✅ Цветовая индикация статуса (критичный = красный, низкий = жёлтый, нормальный = зелёный)

**Использование:**
```vue
<template>
  <InventoryManagement />
</template>

<script setup>
import InventoryManagement from '@/components/store/InventoryManagement.vue'
</script>
```

#### 3. Компонент InventoryRequestsList.vue

**Расположение:** `frontend/src/components/store/InventoryRequestsList.vue`

**Функционал:**
- ✅ Таблица всех заявок на пополнение запасов
- ✅ Фильтрация по статусу (новая, в процессе, выполнена, отменена)
- ✅ Переключение статусов через dropdown
- ✅ Просмотр деталей заявки в модальном окне
- ✅ Редактирование планируемой даты доставки
- ✅ Отмена заявок
- ✅ Отображение типа заявки (ручная / автоматическая)
- ✅ Обновление списка в реальном времени
- ✅ Контроль над критичными заявками

**Использование:**
```vue
<template>
  <InventoryRequestsList />
</template>

<script setup>
import InventoryRequestsList from '@/components/store/InventoryRequestsList.vue'
</script>
```

#### 4. Компонент InventoryAlerts.vue (Виджет для Dashboard)

**Расположение:** `frontend/src/components/store/InventoryAlerts.vue`

**Функционал:**
- ✅ Отображение последних 5 оповещений
- ✅ Счетчик непрочитанных оповещений
- ✅ Счетчик критичных оповещений
- ✅ Цветовая индикация типа оповещения
- ✅ Отметить как прочитанное (при клике)
- ✅ Отметить все как прочитанные (одной кнопкой)
- ✅ Удалить оповещение
- ✅ Относительное время (только что, 5м назад, 2ч назад и т.д.)
- ✅ Автоматическое обновление каждые 30 секунд
- ✅ Ссылка на полный список заявок

**Использование на Dashboard:**
```vue
<template>
  <div class="dashboard-widgets">
    <InventoryAlerts />
  </div>
</template>

<script setup>
import InventoryAlerts from '@/components/store/InventoryAlerts.vue'
</script>
```

## 🔌 Интеграция в существующие компоненты

### Обновление Store.vue

Заменить статические данные на компоненты из API:

```vue
<template>
  <div class="store-view">
    <!-- Вкладки со всеми компонентами -->
    <div class="tabs">
      <button @click="activeTab = 'inventory'" :class="{active: activeTab === 'inventory'}">
        Товары на складе
      </button>
      <button @click="activeTab = 'requests'" :class="{active: activeTab === 'requests'}">
        Заявки на пополнение
      </button>
    </div>
    
    <!-- Содержимое вкладок -->
    <InventoryManagement v-if="activeTab === 'inventory'" />
    <InventoryRequestsList v-if="activeTab === 'requests'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InventoryManagement from '@/components/store/InventoryManagement.vue'
import InventoryRequestsList from '@/components/store/InventoryRequestsList.vue'

const activeTab = ref('inventory')
</script>
```

### Добавление на Dashboard

```vue
<template>
  <div class="dashboard-grid">
    <!-- Существующие компоненты -->
    <div class="widget-row">
      <InventoryAlerts class="widget" />
      <!-- Другие виджеты -->
    </div>
  </div>
</template>

<script setup>
import InventoryAlerts from '@/components/store/InventoryAlerts.vue'
</script>
```

## 📊 Рабочий процесс и сценарии использования

### Сценарий 1: Проверка и пополнение низких запасов

1. **Оператор видит предупреждение на Dashboard**
   - Виджет InventoryAlerts показывает "Товар X критически низко"
   
2. **Переходит в Склад → Заявки на пополнение**
   - Видит полный список с фильтрацией
   
3. **Проверяет товары со статусом "новая"**
   - Нужно подготовить товары к выдаче
   
4. **Обновляет статус заявки на "в процессе"**
   - Товар находится в подготовке
   
5. **После выдачи устанавливает статус "выполнена"**
   - Система автоматически уменьшает `current_count`
   - Создаётся оповещение "Заявка выполнена"

### Сценарий 2: Автоматическое создание заявок

1. **Система периодически проверяет запасы**
   - Кнопка "Проверить низкий запас" в InventoryManagement
   
2. **Для товаров с `current_count < min_stock` создаются заявки**
   - **reason**: "auto" (автоматическая)
   - **status**: "новая"
   
3. **Создаётся оповещение для оператора**
   - Видео на Dashboard в InventoryAlerts
   - Тип: "warning" (оранжевое)

### Сценарий 3: Связь с планированием ремонта

**В планах на будущее:**
- При начале этап "Запрос на получение ЗИП" заявка автоматически создаётся
- При выполнении заявки этап ремонта может продолжиться
- ЗИП отслеживается по всему процессу ремонта

## 🔧 Технические детали

### Расчёт доступного количества

```
availableCount = currentCount - Σ(requestedQuantity для заявок со статусом "новая" или "в_процессе")
```

Это показывает реальное количество товара, которое уже не зарезервировано для активных заявок.

### Автоматическое уменьшение запаса

Когда заявка переводится в статус "выполнена":
1. Находится товар по `inventory_item_id`
2. `current_count -= requested_quantity`
3. Сохраняется в БД
4. Создаётся оповещение типа "success"

## 🌐 Локализация (i18n)

Требуемые ключи в `frontend/src/locales/ru.json`:

```json
{
  "inventory": {
    "warehouseTitle": "Управление складом ЗИП",
    "alertsTitle": "Оповещения по запасам",
    "requestsTitle": "Заявки на пополнение",
    "addItem": "Добавить товар",
    "checkLowStock": "Проверить запасы",
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
    "markAllRead": "Прочитать все"
  }
}
```

## 📈 Результаты и бизнес-ценность

### Для дипломной работы
- ✅ **Объём**: 8+ больших компонентов и функций
- ✅ **Сложность**: Полная интеграция Frontend-Backend с БД
- ✅ **Релевантность**: Тесная связь с существующей системой планирования
- ✅ **Демонстрация навыков**: REST API, SQLAlchemy, Vue 3, управление состоянием

### Практическая ценность
- Эффективное управление запасами ЗИП
- Автоматизация заявок при низких запасах
- Отслеживание истории заявок
- Прямая связь между ремонтом и управлением запасами
- Система оповещений для быстрого реагирования

## 🚀 Следующие шаги

### Краткосрочные (если потребуются)
1. Интеграция с диаграммой Ганта для визуализации заявок
2. Экспорт отчётов по заявкам (PDF/Excel)
3. История изменений со сторонизацией

### Среднесрочные
1. WebSocket для real-time обновлений оповещений
2. Email или SMS оповещения для критичных запасов
3. Планирование автоматических заказов у поставщиков
4. Анализ тенденций использования запасов

## 📞 Поддержка и вопросы

**Архитектура проекта:**
- Backend: Flask + SQLAlchemy + SQLite
- Frontend: Vue 3 + Vite
- Базовые знания REST API и компонентной архитектуры

**Все endpoint'ы документированы в коде с docstring'ами на русском языке.**

---

**Создано:** 08.04.2026  
**Статус:** ✅ Полностью функциональна  
**Готово к использованию в дипломной работе**
