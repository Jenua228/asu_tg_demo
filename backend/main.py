from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from datetime import datetime

import models
from database import engine, SessionLocal, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

# Фиксированные этапы ремонта
DEFAULT_REPAIR_STAGES = [
    "Уведомление о работе №1",
    "Поступление изделия в ремонт",
    "Мойка и чистка изделия",
    "Проверка ЭД",
    "Дефектация изделия в собранном виде",
    "Разборка изделия на агрегаты и СЧ",
    "Очистка и мойка блоков, СЧ",
    "Обдув сжатым воздухом",
    "Дефектация на СТНО блоков и узлов",
    "Разборка, ремонт и контроль",
    "Запрос на получение ЗИП со склада",
    "Сборка, настройка на СТНО, проверка и контроль",
    "Дефектация на СТНО блоков и узлов",
    "Разборка, ремонт и контроль",
    "Сборка, настройка на СТНО, проверка и контроль",
    "Поступление на склад готовой продукции"
]

# ==================== TASK HELPERS ====================

def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "start_date": task.start_date.isoformat() if task.start_date else None,
        "end_date": task.end_date.isoformat() if task.end_date else None,
        "status": task.status,
        "color": task.color,
        "row_index": task.row_index,
        "parent_id": task.parent_id,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "outgoing_connections": [conn_to_dict(c) for c in task.outgoing_connections],
        "incoming_connections": [conn_to_dict(c) for c in task.incoming_connections]
    }


def conn_to_dict(conn):
    return {
        "id": conn.id,
        "from_task_id": conn.from_task_id,
        "to_task_id": conn.to_task_id,
        "arrow_color": conn.arrow_color,
        "arrow_style": conn.arrow_style,
        "arrow_type": conn.arrow_type
    }


def report_to_dict(record):
    return {
        "id": record.id,
        "isSectionHeader": record.is_section_header,
        "sectionTitle": record.section_title or "",
        "receivingDate": record.receiving_date or "",
        "division": record.division or "",
        "nameRETIndex": record.name_ret_index or "",
        "factoryNumber": record.factory_number or "",
        "category": record.category or "",
        "makeDate": record.make_date or "",
        "failureDate": record.failure_date or "",
        "repairType": record.repair_type or "",
        "dueDate": record.due_date or "",
        "capitalRepairs": record.capital_repairs or "",
        "militaryRepairs": record.military_repairs or "",
        "hoursFromStart": record.hours_from_start or "",
        "hoursFromLastRepair": record.hours_from_last_repair or "",
        "responsibleRepair": record.responsible_repair or "",
        "beginRepairDate": record.begin_repair_date or "",
        "workType": record.work_type or "",
        "laborCost": record.labor_cost or "",
        "usedZIP": record.used_zip or "",
        "plannedEndDate": record.planned_end_date or "",
        "endRepairDate": record.end_repair_date or "",
        "issueDate": record.issue_date or "",
        "responsibleTransfer": record.responsible_transfer or "",
        "destination": record.destination or "",
        "daysCount": record.days_count,
        "tcr": record.tcr or "",
        "plannedStartDate": record.planned_start_date or "",
        "status": record.status or "не начато",
        "color": record.color or "#4A90D9",
        "predecessors": record.predecessors or "",
        "successors": record.successors or "",
        "division": record.division or "",
        "plannedHours": record.planned_hours or "",
        "spentHours": record.spent_hours or "",
        "comments": record.comments or ""
    }

def repair_detail_to_dict(detail):
    return {
        "id": detail.id,
        "parentReportId": detail.parent_report_id,
        "productName": detail.product_name or "",
        "serialNumber": detail.serial_number or "",
        "parentName": detail.parent_name or "",
        "stageName": detail.stage_name or "",
        "division": detail.division or "",
        "startDate": detail.start_date or "",
        "plannedStartDate": detail.planned_start_date,
        "plannedEndDate": detail.planned_end_date,
        "endDate": detail.end_date or "",
        "status": detail.status or "не начато",
        "visualSigns": detail.visual_signs or "",
        "peopleCount": detail.people_count or "",
        "usedZip": detail.used_zip or "",
        "plannedHours": detail.planned_hours or "",
        "spentHours": detail.spent_hours or "",
        "predecessor": detail.predecessor or "",
        "color": detail.color or "#4A90D9",
        "rowIndex": detail.row_index or 0,
        "responsible": detail.responsible or "",
        "comment": detail.comment or ""
    }

# ========== TASK ENDPOINTS ==========

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Get all tasks with their connections"""
    db = SessionLocal()
    try:
        tasks = db.query(models.Task).all()
        return jsonify([task_to_dict(t) for t in tasks])
    finally:
        db.close()


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a specific task by ID"""
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task_to_dict(task))
    finally:
        db.close()


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        db_task = models.Task(
            title=data.get("title"),
            description=data.get("description"),
            start_date=datetime.fromisoformat(data.get("start_date").replace("Z", "+00:00")) if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data.get("end_date").replace("Z", "+00:00")) if data.get("end_date") else None,
            status=data.get("status", "not started"),
            color=data.get("color", "#4A90D9"),
            row_index=data.get("row_index", 0),
            parent_id=data.get("parent_id")
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return jsonify(task_to_dict(db_task)), 201
    finally:
        db.close()


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task"""
    db = SessionLocal()
    try:
        db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not db_task:
            return jsonify({"error": "Task not found"}), 404
        
        data = request.get_json()
        
        if "title" in data:
            db_task.title = data["title"]
        if "description" in data:
            db_task.description = data["description"]
        if "start_date" in data:
            db_task.start_date = datetime.fromisoformat(data["start_date"].replace("Z", "+00:00"))
        if "end_date" in data:
            db_task.end_date = datetime.fromisoformat(data["end_date"].replace("Z", "+00:00"))
        if "status" in data:
            db_task.status = data["status"]
        if "color" in data:
            db_task.color = data["color"]
        if "row_index" in data:
            db_task.row_index = data["row_index"]
        if "parent_id" in data:
            # Prevent circular reference
            if data["parent_id"] != task_id:
                db_task.parent_id = data["parent_id"]
        
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
        return jsonify(task_to_dict(db_task))
    finally:
        db.close()


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task"""
    db = SessionLocal()
    try:
        db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not db_task:
            return jsonify({"error": "Task not found"}), 404
        
        db.delete(db_task)
        db.commit()
        return jsonify({"message": "Task deleted successfully"})
    finally:
        db.close()


# ========== CONNECTION ENDPOINTS ==========

@app.route("/api/connections", methods=["GET"])
def get_connections():
    """Get all task connections"""
    db = SessionLocal()
    try:
        connections = db.query(models.TaskConnection).all()
        return jsonify([conn_to_dict(c) for c in connections])
    finally:
        db.close()


@app.route("/api/connections", methods=["POST"])
def create_connection():
    """Create a new connection between tasks"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        from_task_id = data.get("from_task_id")
        to_task_id = data.get("to_task_id")
        
        # Verify both tasks exist
        from_task = db.query(models.Task).filter(models.Task.id == from_task_id).first()
        to_task = db.query(models.Task).filter(models.Task.id == to_task_id).first()
        
        if not from_task or not to_task:
            return jsonify({"error": "One or both tasks not found"}), 404
        
        # Check if connection already exists
        existing = db.query(models.TaskConnection).filter(
            models.TaskConnection.from_task_id == from_task_id,
            models.TaskConnection.to_task_id == to_task_id
        ).first()
        
        if existing:
            return jsonify({"error": "Connection already exists"}), 400
        
        db_connection = models.TaskConnection(
            from_task_id=from_task_id,
            to_task_id=to_task_id,
            arrow_color=data.get("arrow_color", "#666666"),
            arrow_style=data.get("arrow_style", "solid"),
            arrow_type=data.get("arrow_type", "finish-to-start")
        )
        db.add(db_connection)
        db.commit()
        db.refresh(db_connection)
        return jsonify(conn_to_dict(db_connection)), 201
    finally:
        db.close()


@app.route("/api/connections/<int:connection_id>", methods=["PUT"])
def update_connection(connection_id):
    """Update a connection's arrow style"""
    db = SessionLocal()
    try:
        db_connection = db.query(models.TaskConnection).filter(models.TaskConnection.id == connection_id).first()
        if not db_connection:
            return jsonify({"error": "Connection not found"}), 404
        
        data = request.get_json()
        
        if "arrow_color" in data:
            db_connection.arrow_color = data["arrow_color"]
        if "arrow_style" in data:
            db_connection.arrow_style = data["arrow_style"]
        if "arrow_type" in data:
            db_connection.arrow_type = data["arrow_type"]
        
        db.commit()
        db.refresh(db_connection)
        return jsonify(conn_to_dict(db_connection))
    finally:
        db.close()


@app.route("/api/connections/<int:connection_id>", methods=["DELETE"])
def delete_connection(connection_id):
    """Delete a connection"""
    db = SessionLocal()
    try:
        db_connection = db.query(models.TaskConnection).filter(models.TaskConnection.id == connection_id).first()
        if not db_connection:
            return jsonify({"error": "Connection not found"}), 404
        
        db.delete(db_connection)
        db.commit()
        return jsonify({"message": "Connection deleted successfully"})
    finally:
        db.close()


# ========== REPORT RECORDS ENDPOINTS ==========

@app.route("/api/reports", methods=["GET"])
def get_reports():
    """Get all report records"""
    db = SessionLocal()
    try:
        records = db.query(models.ReportRecord).order_by(models.ReportRecord.id).all()
        return jsonify([report_to_dict(r) for r in records])
    finally:
        db.close()


@app.route("/api/reports", methods=["POST"])
def create_report():
    """Create a new report record"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        db_record = models.ReportRecord(
            is_section_header=data.get("isSectionHeader", False),
            section_title=data.get("sectionTitle"),
            receiving_date=data.get("receivingDate"),
            division=data.get("division"),
            name_ret_index=data.get("nameRETIndex"),
            factory_number=data.get("factoryNumber"),
            category=data.get("category"),
            make_date=data.get("makeDate"),
            failure_date=data.get("failureDate"),
            repair_type=data.get("repairType"),
            due_date=data.get("dueDate"),
            capital_repairs=data.get("capitalRepairs"),
            military_repairs=data.get("militaryRepairs"),
            hours_from_start=data.get("hoursFromStart"),
            hours_from_last_repair=data.get("hoursFromLastRepair"),
            responsible_repair=data.get("responsibleRepair"),
            begin_repair_date=data.get("beginRepairDate"),
            work_type=data.get("workType"),
            labor_cost=data.get("laborCost"),
            used_zip=data.get("usedZIP"),
            end_repair_date=data.get("endRepairDate"),
            issue_date=data.get("issueDate"),
            responsible_transfer=data.get("responsibleTransfer"),
            destination=data.get("destination"),
            tcr=data.get("tcr"),
            planned_start_date=data.get("plannedStartDate"),
            status=data.get("status", "не начато"),
            color=data.get("color", "#4A90D9"),
            comments=data.get("comments")
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return jsonify(report_to_dict(db_record)), 201
    finally:
        db.close()


@app.route("/api/reports/<int:record_id>", methods=["PUT"])
def update_report(record_id):
    """Update an existing report record"""
    db = SessionLocal()
    try:
        db_record = db.query(models.ReportRecord).filter(models.ReportRecord.id == record_id).first()
        if not db_record:
            return jsonify({"error": "Record not found"}), 404
        
        data = request.get_json()
        
        if "isSectionHeader" in data:
            db_record.is_section_header = data["isSectionHeader"]
        if "sectionTitle" in data:
            db_record.section_title = data["sectionTitle"]
        if "receivingDate" in data:
            db_record.receiving_date = data["receivingDate"]
        if "division" in data:
            db_record.division = data["division"]
        if "nameRETIndex" in data:
            db_record.name_ret_index = data["nameRETIndex"]
        if "factoryNumber" in data:
            db_record.factory_number = data["factoryNumber"]
        if "category" in data:
            db_record.category = data["category"]
        if "makeDate" in data:
            db_record.make_date = data["makeDate"]
        if "failureDate" in data:
            db_record.failure_date = data["failureDate"]
        if "repairType" in data:
            db_record.repair_type = data["repairType"]
        if "dueDate" in data:
            db_record.due_date = data["dueDate"]
        if "capitalRepairs" in data:
            db_record.capital_repairs = data["capitalRepairs"]
        if "militaryRepairs" in data:
            db_record.military_repairs = data["militaryRepairs"]
        if "hoursFromStart" in data:
            db_record.hours_from_start = data["hoursFromStart"]
        if "hoursFromLastRepair" in data:
            db_record.hours_from_last_repair = data["hoursFromLastRepair"]
        if "responsibleRepair" in data:
            db_record.responsible_repair = data["responsibleRepair"]
        if "beginRepairDate" in data:
            db_record.begin_repair_date = data["beginRepairDate"]
        if "workType" in data:
            db_record.work_type = data["workType"]
        if "laborCost" in data:
            db_record.labor_cost = data["laborCost"]
        if "usedZIP" in data:
            db_record.used_zip = data["usedZIP"]
        if "endRepairDate" in data:
            db_record.end_repair_date = data["endRepairDate"]
        if "issueDate" in data:
            db_record.issue_date = data["issueDate"]
        if "responsibleTransfer" in data:
            db_record.responsible_transfer = data["responsibleTransfer"]
        if "destination" in data:
            db_record.destination = data["destination"]
        if "tcr" in data:
            db_record.tcr = data["tcr"]
        if "plannedStartDate" in data:
            db_record.planned_start_date = data["plannedStartDate"]
        if "status" in data:
            db_record.status = data["status"]
        if "color" in data:
            db_record.color = data["color"]
        if "comments" in data:
            db_record.comments = data["comments"]
        if "plannedEndDate" in data:
            db_record.planned_end_date = data["plannedEndDate"]
        
        db_record.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_record)
        return jsonify(report_to_dict(db_record))
    finally:
        db.close()


@app.route("/api/reports/<int:record_id>", methods=["DELETE"])
def delete_report(record_id):
    """Delete a report record"""
    db = SessionLocal()
    try:
        db_record = db.query(models.ReportRecord).filter(models.ReportRecord.id == record_id).first()
        if not db_record:
            return jsonify({"error": "Record not found"}), 404
        
        db.delete(db_record)
        db.commit()
        return jsonify({"message": "Record deleted successfully"})
    finally:
        db.close()


@app.route("/api/reports/reset", methods=["POST"])
def reset_reports():
    """Reset reports to default data from JSON"""
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(models.ReportRecord).delete()
        db.commit()
        return jsonify({"message": "Reports cleared. Load initial data from frontend."})
    finally:
        db.close()


# ========== UTILITY ENDPOINTS ==========

@app.route("/api/tasks/seed", methods=["POST"])
def seed_demo_data():
    """Seed database with demo data"""
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(models.TaskConnection).delete()
        db.query(models.Task).delete()
        db.commit()
        
        # Create parent tasks first
        parent_dev = models.Task(
            title="Development Phase",
            description="All development work",
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 3, 20),
            progress=40,
            color="#673AB7",
            row_index=0
        )
        db.add(parent_dev)
        db.commit()
        db.refresh(parent_dev)
                
        for task in tasks:
            db.add(task)
        db.commit()
        
        # Refresh to get IDs
        for task in tasks:
            db.refresh(task)
        
        # Create connections
        connections = [
            models.TaskConnection(from_task_id=tasks[0].id, to_task_id=tasks[1].id, arrow_color="#4CAF50"),
            models.TaskConnection(from_task_id=tasks[1].id, to_task_id=tasks[2].id, arrow_color="#2196F3"),
            models.TaskConnection(from_task_id=tasks[1].id, to_task_id=tasks[3].id, arrow_color="#2196F3", arrow_style="dashed"),
            models.TaskConnection(from_task_id=tasks[2].id, to_task_id=tasks[4].id, arrow_color="#9C27B0"),
            models.TaskConnection(from_task_id=tasks[3].id, to_task_id=tasks[4].id, arrow_color="#FF9800"),
            models.TaskConnection(from_task_id=tasks[4].id, to_task_id=tasks[5].id, arrow_color="#F44336"),
        ]
        
        for conn in connections:
            db.add(conn)
        db.commit()
        
        return jsonify({
            "message": "Demo data seeded successfully",
            "tasks_created": len(tasks) + 1,
            "connections_created": len(connections)
        })
    finally:
        db.close()


@app.route("/api/gantt-data", methods=["GET"])
def get_gantt_data():
    """Get report records formatted for Gantt chart"""
    db = SessionLocal()
    try:
        records = db.query(models.ReportRecord).filter(
            models.ReportRecord.is_section_header == False
        ).all()
        
        gantt_tasks = []
        for record in records:
            # Вычисляем количество дней
            days = None
            if record.begin_repair_date and record.end_repair_date:
                try:
                    start = datetime.strptime(record.begin_repair_date, "%d.%m.%Y")
                    end = datetime.strptime(record.end_repair_date, "%d.%m.%Y")
                    days = (end - start).days + 1
                except:
                    days = None
            
            gantt_tasks.append({
                "id": record.id,
                "title": record.name_ret_index or "",
                "start_date": record.begin_repair_date or "",
                "end_date": record.end_repair_date or "",
                "division": record.division or "",
                "status": record.status or "не начато",
                "color": record.color or "#4A90D9",
                "planned_hours": record.labor_cost or "",  
                "spent_hours": record.spent_hours or "",
                "predecessors": record.predecessors or "",
                "successors": record.successors or ""
            })
        
        return jsonify(gantt_tasks)
    finally:
        db.close()

@app.route("/api/gantt", methods=["GET"])
def get_gantt_full():
    """Get report records with connections for Gantt chart (read-only)"""
    db = SessionLocal()
    try:
        # 1. Получаем все записи (не заголовки секций)
        records = db.query(models.ReportRecord).filter(
            models.ReportRecord.is_section_header == False
        ).all()
        
        # 2. Получаем все связи
        connections = db.query(models.ReportConnection).all()
        
        # 3. Формируем задачи для Ганта
        gantt_tasks = []
        for record in records:
            gantt_tasks.append({
                "id": record.id,
                "title": record.name_ret_index or "",
                "start_date": record.begin_repair_date or "",
                "end_date": record.end_repair_date or "",
                "status": record.status or "не начато",
                "color": record.color or "#4A90D9",
            })
        
        # 4. Формируем связи
        gantt_connections = []
        for conn in connections:
            gantt_connections.append({
                "id": conn.id,
                "from_task_id": conn.from_record_id,
                "to_task_id": conn.to_record_id,
                "arrow_color": conn.arrow_color,
                "arrow_style": conn.arrow_style,
                "arrow_type": conn.arrow_type
            })
        
        return jsonify({
            "tasks": gantt_tasks,
            "connections": gantt_connections
        })
    finally:
        db.close()

@app.route("/api/gantt-data/<int:record_id>", methods=["PUT"])
def update_gantt_record(record_id):
    """Update dates for a report record (for Gantt chart drag)"""
    db = SessionLocal()
    try:
        record = db.query(models.ReportRecord).filter(
            models.ReportRecord.id == record_id
        ).first()
        
        if not record:
            return jsonify({"error": "Record not found"}), 404
        
        data = request.get_json()
        
        # Обновляем даты если они переданы
        if "start_date" in data:
            # Преобразуем из ISO в формат ДД.ММ.ГГГГ
            try:
                dt = datetime.fromisoformat(data["start_date"].replace("Z", "+00:00"))
                record.begin_repair_date = dt.strftime("%d.%m.%Y")
            except:
                pass
        
        if "end_date" in data:
            try:
                dt = datetime.fromisoformat(data["end_date"].replace("Z", "+00:00"))
                record.end_repair_date = dt.strftime("%d.%m.%Y")
            except:
                pass

        if "status" in data:
            record.status = data["status"]
        if "color" in data:
            record.color = data["color"]
        
        db.commit()
        db.refresh(record)
        
        return jsonify({
            "id": record.id,
            "title": record.name_ret_index,
            "start_date": record.begin_repair_date,
            "end_date": record.end_repair_date,
            "status": record.status,
            "color": record.color
        })
    finally:
        db.close()

# ========== REPORT CONNECTIONS (для диаграммы Ганта) ==========

def report_conn_to_dict(conn):
    return {
        "id": conn.id,
        "from_task_id": conn.from_record_id,
        "to_task_id": conn.to_record_id,
        "arrow_color": conn.arrow_color,
        "arrow_style": conn.arrow_style,
        "arrow_type": conn.arrow_type
    }


@app.route("/api/report-connections", methods=["GET"])
def get_report_connections():
    """Get all report connections"""
    db = SessionLocal()
    try:
        connections = db.query(models.ReportConnection).all()
        return jsonify([report_conn_to_dict(c) for c in connections])
    finally:
        db.close()


@app.route("/api/report-connections", methods=["POST"])
def create_report_connection():
    """Create a connection between report records"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        from_id = data.get("from_task_id")
        to_id = data.get("to_task_id")
        
        # Проверяем, что записи существуют в report_records
        from_record = db.query(models.ReportRecord).filter(models.ReportRecord.id == from_id).first()
        to_record = db.query(models.ReportRecord).filter(models.ReportRecord.id == to_id).first()
        
        if not from_record or not to_record:
            return jsonify({"error": "One or both records not found"}), 404
        
        # Проверяем, нет ли уже такой связи
        existing = db.query(models.ReportConnection).filter(
            models.ReportConnection.from_record_id == from_id,
            models.ReportConnection.to_record_id == to_id
        ).first()
        
        if existing:
            return jsonify({"error": "Connection already exists"}), 400
        
        db_connection = models.ReportConnection(
            from_record_id=from_id,
            to_record_id=to_id,
            arrow_color=data.get("arrow_color", "#666666"),
            arrow_style=data.get("arrow_style", "solid"),
            arrow_type=data.get("arrow_type", "finish-to-start")
        )
        db.add(db_connection)
        db.commit()
        db.refresh(db_connection)
        return jsonify(report_conn_to_dict(db_connection)), 201
    finally:
        db.close()


@app.route("/api/report-connections/<int:connection_id>", methods=["PUT"])
def update_report_connection(connection_id):
    """Update a report connection"""
    db = SessionLocal()
    try:
        db_connection = db.query(models.ReportConnection).filter(
            models.ReportConnection.id == connection_id
        ).first()
        
        if not db_connection:
            return jsonify({"error": "Connection not found"}), 404
        
        data = request.get_json()
        
        if "arrow_color" in data:
            db_connection.arrow_color = data["arrow_color"]
        if "arrow_style" in data:
            db_connection.arrow_style = data["arrow_style"]
        if "arrow_type" in data:
            db_connection.arrow_type = data["arrow_type"]
        
        db.commit()
        db.refresh(db_connection)
        return jsonify(report_conn_to_dict(db_connection))
    finally:
        db.close()


@app.route("/api/report-connections/<int:connection_id>", methods=["DELETE"])
def delete_report_connection(connection_id):
    """Delete a report connection"""
    db = SessionLocal()
    try:
        db_connection = db.query(models.ReportConnection).filter(
            models.ReportConnection.id == connection_id
        ).first()
        
        if not db_connection:
            return jsonify({"error": "Connection not found"}), 404
        
        db.delete(db_connection)
        db.commit()
        return jsonify({"message": "Connection deleted successfully"})
    finally:
        db.close()

# ========== REPAIR DETAILS (Детализация ремонта) ==========

@app.route("/api/repair-details/<int:report_id>", methods=["GET"])
def get_repair_details(report_id):
    """Получить все этапы ремонта для конкретной записи"""
    db = SessionLocal()
    try:
        # Проверяем, существует ли родительская запись
        parent = db.query(models.ReportRecord).filter(
            models.ReportRecord.id == report_id
        ).first()
        
        if not parent:
            return jsonify({"error": "Parent report not found"}), 404
        
        # Получаем детализацию
        details = db.query(models.RepairDetail).filter(
            models.RepairDetail.parent_report_id == report_id
        ).order_by(models.RepairDetail.row_index).all()

        # ОБНОВЛЯЕМ данные из родительской записи при каждом открытии
        for detail in details:
            detail.product_name = parent.name_ret_index
            detail.serial_number = parent.factory_number
        
        db.commit()
        
        return jsonify({
            "parentReport": report_to_dict(parent),
            "details": [repair_detail_to_dict(d) for d in details]
        })
    finally:
        db.close()

@app.route("/api/repair-details/<int:report_id>", methods=["POST"])
def create_repair_detail(report_id):
    """Create a new repair detail for a report"""
    db = SessionLocal()
    try:
        # Проверяем существование родительского отчёта
        parent = db.query(models.ReportRecord).filter(models.ReportRecord.id == report_id).first()
        if not parent:
            return jsonify({"error": "Report not found"}), 404
        
        data = request.get_json()
        
        detail = models.RepairDetail(
            parent_report_id=report_id,
            product_name=parent.name_ret_index,
            serial_number=parent.factory_number,
            stage_name=data.get("stageName", "Новый этап"),
            division=data.get("division", ""),
            status=data.get("status", "предстоящая"),
            row_index=len(parent.repair_details)
        )
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return jsonify(repair_detail_to_dict(detail)), 201
    finally:
        db.close()

@app.route("/api/repair-details/<int:report_id>/init", methods=["POST"])
def init_repair_details(report_id):
    """Инициализировать этапы ремонта для записи (создать все 16 этапов)"""
    db = SessionLocal()
    try:
        # Проверяем родительскую запись
        parent = db.query(models.ReportRecord).filter(
            models.ReportRecord.id == report_id
        ).first()
        
        if not parent:
            return jsonify({"error": "Parent report not found"}), 404
        
        # Проверяем, есть ли уже этапы
        existing = db.query(models.RepairDetail).filter(
            models.RepairDetail.parent_report_id == report_id
        ).count()
        
        if existing > 0:
            return jsonify({"message": "Details already exist", "count": existing})
        
        # Создаём все этапы
        first_stage_name = DEFAULT_REPAIR_STAGES[0]
        for index, stage_name in enumerate(DEFAULT_REPAIR_STAGES):
            detail = models.RepairDetail(
                parent_report_id=report_id,
                product_name=parent.name_ret_index,
                serial_number=parent.factory_number,
                parent_name=first_stage_name,
                stage_name=stage_name,
                division="",
                start_date="",
                end_date="",
                status="не начато",
                used_zip=parent.used_zip if index == 10 else "",  # ЗИП только для этапа запроса
                predecessor=DEFAULT_REPAIR_STAGES[index - 1] if index > 0 else "",
                row_index=index
            )
            db.add(detail)
        
        db.commit()
        
        return jsonify({
            "message": "Repair details initialized",
            "count": len(DEFAULT_REPAIR_STAGES)
        }), 201
    finally:
        db.close()


@app.route("/api/repair-details/item/<int:detail_id>", methods=["PUT"])
def update_repair_detail(detail_id):
    """Обновить конкретный этап ремонта"""
    db = SessionLocal()
    try:
        detail = db.query(models.RepairDetail).filter(
            models.RepairDetail.id == detail_id
        ).first()
        
        if not detail:
            return jsonify({"error": "Detail not found"}), 404
        
        data = request.get_json()
        
        # Обновляем поля
        if "division" in data:
            detail.division = data["division"]
        if "startDate" in data:
            detail.start_date = data["startDate"]
        if "endDate" in data:
            detail.end_date = data["endDate"]
        if "status" in data:
            detail.status = data["status"]
        if "visualSigns" in data:
            detail.visual_signs = data["visualSigns"]
        if "peopleCount" in data:
            detail.people_count = data["peopleCount"]
        if "usedZip" in data:
            detail.used_zip = data["usedZip"]
        if "plannedStartDate" in data:
            detail.planned_start_date = data["plannedStartDate"]
        if "plannedEndDate" in data:
            detail.planned_end_date = data["plannedEndDate"]
        if "plannedHours" in data:
            detail.planned_hours = data["plannedHours"]
        if "spentHours" in data:
            detail.spent_hours = data["spentHours"]
        if "predecessor" in data:
            detail.predecessor = data["predecessor"]
        if "color" in data:
            detail.color = data["color"]
        if "stageName" in data:
            detail.stage_name = data["stageName"]
        if "parentName" in data:
            detail.parent_name = data["parentName"]
        if 'responsible' in data:
            detail.responsible = data['responsible']
        if "comment" in data:
            detail.comment = data["comment"]
        
        detail.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(detail)
        
        return jsonify(repair_detail_to_dict(detail))
    finally:
        db.close()


@app.route("/api/repair-details/item/<int:detail_id>", methods=["DELETE"])
def delete_repair_detail(detail_id):
    """Удалить этап ремонта"""
    db = SessionLocal()
    try:
        detail = db.query(models.RepairDetail).filter(
            models.RepairDetail.id == detail_id
        ).first()
        
        if not detail:
            return jsonify({"error": "Detail not found"}), 404
        
        db.delete(detail)
        db.commit()
        
        return jsonify({"message": "Detail deleted"})
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
