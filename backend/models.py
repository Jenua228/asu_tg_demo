from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# ==================== GANTT MODELS ====================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    progress = Column(Float, default=0.0)  # 0-100%
    color = Column(String(50), default="#4A90D9")
    row_index = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Parent-child relationship
    parent = relationship("Task", remote_side=[id], back_populates="children")
    children = relationship("Task", back_populates="parent", cascade="all")

    # Relationships for connections
    outgoing_connections = relationship(
        "TaskConnection",
        foreign_keys="TaskConnection.from_task_id",
        back_populates="from_task",
        cascade="all, delete-orphan"
    )
    incoming_connections = relationship(
        "TaskConnection",
        foreign_keys="TaskConnection.to_task_id",
        back_populates="to_task",
        cascade="all, delete-orphan"
    )


class TaskConnection(Base):
    __tablename__ = "task_connections"

    id = Column(Integer, primary_key=True, index=True)
    from_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    to_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    
    # Arrow customization
    arrow_color = Column(String(50), default="#666666")
    arrow_style = Column(String(50), default="solid")  # solid, dashed, dotted
    arrow_type = Column(String(50), default="finish-to-start")  # finish-to-start, start-to-start, finish-to-finish, start-to-finish
    
    from_task = relationship("Task", foreign_keys=[from_task_id], back_populates="outgoing_connections")
    to_task = relationship("Task", foreign_keys=[to_task_id], back_populates="incoming_connections")


# ==================== REPORTS MODELS ====================

class ReportRecord(Base):
    """Модель для записей таблицы отчётов (ремонт и ТО)"""
    __tablename__ = "report_records"

    id = Column(Integer, primary_key=True, index=True)
    is_section_header = Column(Boolean, default=False)
    section_title = Column(String(500))  # Название секции для заголовков
    
    # Основные поля
    tcr = Column(String(100))  # ТЦР
    receiving_date = Column(String(50))  # Дата приема на ТО, в ремонт
    division = Column(String(255))  # Подразделение
    name_ret_index = Column(String(255))  # Наименование, индекс РЭТ
    factory_number = Column(String(100))  # Заводской номер
    category = Column(String(50))  # Категория
    make_date = Column(String(50))  # Дата изготовления
    failure_date = Column(String(50))  # Дата выхода из строя
    repair_type = Column(String(255))  # Вид требуемого ремонта
    due_date = Column(String(50))  # Срок выполнения работ
    planned_start_date = Column(String(50))  # Планируемая дата начала ремонта
    
    # Количество ремонтов
    capital_repairs = Column(String(50))  # Капитальных
    military_repairs = Column(String(50))  # Войсковых
    
    # Количество часов
    hours_from_start = Column(String(50))  # С начала эксплуатации
    hours_from_last_repair = Column(String(50))  # После последнего ремонта
    
    # Исполнение
    responsible_repair = Column(String(255))  # Ответственный за ремонт
    begin_repair_date = Column(String(50))  # Дата начала работ
    work_type = Column(String(255))  # Вид выполненных работ
    planned_hours = Column(String(50))  # Запланировано человеко-часов
    spent_hours = Column(String(50))  # Фактически человеко-часов
    labor_cost = Column(String(50))  # Трудозатраты
    used_zip = Column(Text)  # Использованный ЗИП
    planned_end_date = Column(String(50))  # Планируемая дата окончания ремонта
    end_repair_date = Column(String(50))  # Дата окончания работ
    issue_date = Column(String(50))  # Дата выдачи
    responsible_transfer = Column(String(255))  # Ответственный за передачу
    destination = Column(Text)  # Пункт назначения
    days_count = Column(Integer, nullable=True)  # Кол-во дней (вычисляется: end_repair_date - begin_repair_date)
    status = Column(String(50), default="не начато")  # Статус: не начато, выполняется, выполнено, отменено
    color = Column(String(50), default="#4A90D9")  # Цвет для диаграммы Ганта
    predecessors = Column(Text, nullable=True)  # Предшественники (JSON строка с ID задач или названиями)
    successors = Column(Text, nullable=True)  # Последователи (JSON строка с ID задач или названиями)
    comments = Column(Text, nullable=True)  # Комментарии

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportConnection(Base):
    """Связи между записями отчётов для диаграммы Ганта"""
    __tablename__ = "report_connections"

    id = Column(Integer, primary_key=True, index=True)
    from_record_id = Column(Integer, ForeignKey("report_records.id", ondelete="CASCADE"), nullable=False)
    to_record_id = Column(Integer, ForeignKey("report_records.id", ondelete="CASCADE"), nullable=False)
    
    arrow_color = Column(String(50), default="#666666")
    arrow_style = Column(String(50), default="solid")
    arrow_type = Column(String(50), default="finish-to-start")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class RepairDetail(Base):
    """Детализация ремонта по конкретному изделию (этапы работ)"""
    __tablename__ = "repair_details"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с родительской записью из report_records
    parent_report_id = Column(Integer, ForeignKey("report_records.id", ondelete="CASCADE"), nullable=False)
    
    # Данные из родительской записи (копируются для удобства)
    product_name = Column(String(255))       # Название изделия (из name_ret_index)
    serial_number = Column(String(100))      # Серийный номер (из factory_number)
    parent_name = Column(String(255))        # Название родительской записи
    
    # Название этапа (фиксированный список)
    stage_name = Column(String(500), nullable=False)
    
    # Остальные поля
    division = Column(String(255))           # Участок/цех
    start_date = Column(String(50))          # Дата начала
    end_date = Column(String(50))            # Дата окончания
    planned_start_date = Column(String(50))    # План. дата начала
    planned_end_date = Column(String(50)) 
    status = Column(String(50), default="не начато")  # Статус
    visual_signs = Column(Text)              # Признаки/визуальные
    people_count = Column(String(50))        # Количество человек
    used_zip = Column(Text)                  # Израсходовано ЗИП
    planned_hours = Column(String(50))       # Запланировано (часов)
    spent_hours = Column(String(50))         # Потрачено (часов)
    predecessor = Column(String(255))        # Предыдущая (название этапа)
    comment = Column(Text, nullable=True)  # Комментарий
    
    # Для диаграммы Ганта
    color = Column(String(50), default="#4A90D9")
    row_index = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с родительской записью
    parent_report = relationship("ReportRecord", backref="repair_details")
    responsible = Column(String(200), default='')  # Ответственный за задачу


# ==================== INVENTORY MODELS (СКЛАД ЗИП) ====================

class InventoryItem(Base):
    """Элемент на складе ЗИП - описание товара и его остаток"""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(100), unique=True, nullable=False)  # Артикул
    name_rus = Column(String(500), nullable=False)  # Название на русском
    name_eng = Column(String(500), nullable=True)  # Название на английском
    image_Name = Column('imgName', String(255), nullable=True)  # Имя файла картинки (например, "part123.jpg")
    current_count = Column(Integer, default=0)  # Текущее количество на складе
    min_stock = Column(Integer, default=0)  # Минимально допустимое количество
    storage_name = Column(String(200), nullable=True)  # Название склада/места хранения
    comment = Column(Text, nullable=True)  # Комментарий
    pdf_url = Column(String(500), nullable=True)  # URL на техническую документацию
    unit_measurement = Column(String(50), default="шт.")  # Единица измерения (шт., кг, м, л и т.д.)
    reserved_count = Column(Integer, default=0)  # Зарезервированное количество

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    inventory_requests = relationship("InventoryRequest", back_populates="inventory_item", cascade="all, delete-orphan")


class InventoryRequest(Base):
    """Заявка на пополнение запасов ЗИП"""
    __tablename__ = "inventory_requests"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False)
    
    requested_quantity = Column(Integer, nullable=False)  # Запрашиваемое количество
    
    # Тип заявки: manual (по кнопке) | auto (автоматическая по минимальному запасу)
    reason = Column(String(50), default="manual")
    
    # Статус заявки
    status = Column(String(50), default="новая")  # новая|в_процессе|выполнена|отменена
    
    # Связь с этапом ремонта (может быть заявка и без привязки к ремонту)
    related_repair_detail_id = Column(Integer, ForeignKey("repair_details.id", ondelete="SET NULL"), nullable=True)
    
    # Связь с записью отчета (из какого ремонта идет заявка)
    related_report_id = Column(Integer, ForeignKey("report_records.id", ondelete="SET NULL"), nullable=True)
    
    # Кто создал заявку
    created_by = Column(String(200), nullable=True)
    
    # Была ли отправлена уведомление на информационную панель
    notification_sent = Column(Boolean, default=False)
    
    # Дополнительные даты
    planned_delivery_date = Column(String(50), nullable=True)  # Планируемая дата доставки
    actual_delivery_date = Column(String(50), nullable=True)  # Фактическая дата выдачи со склада
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    inventory_item = relationship("InventoryItem", back_populates="inventory_requests")
    alerts = relationship("InventoryAlert", back_populates="request", cascade="all, delete-orphan")


class InventoryAlert(Base):
    """Уведомления по заявкам и событиям на складе"""
    __tablename__ = "inventory_alerts"

    id = Column(Integer, primary_key=True, index=True)
    
    inventory_request_id = Column(Integer, ForeignKey("inventory_requests.id", ondelete="CASCADE"), nullable=True)
    
    # Тип уведомления: info|warning|critical|success
    alert_type = Column(String(50), default="info")
    
    # Тип события: new_request|low_stock|request_completed|auto_request_created
    event_type = Column(String(100), nullable=False)
    
    # Сообщение
    message = Column(Text, nullable=False)
    
    # Статус прочтения
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь с заявкой
    request = relationship("InventoryRequest", back_populates="alerts")