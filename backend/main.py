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


# ========== INVENTORY ITEMS (УПРАВЛЕНИЕ ЗАПАСАМИ ЗИП) ==========

def inventory_item_to_dict(item):
    """Преобразовать InventoryItem в JSON с расчетом доступного количества"""
    db = SessionLocal()
    try:
        # Рассчитываем доступное количество = текущее - сумма активных заявок
        active_requests = db.query(models.InventoryRequest).filter(
            models.InventoryRequest.inventory_item_id == item.id,
            models.InventoryRequest.status.in_(["новая", "в_процессе"])
        ).all()
        
        requested_total = sum(req.requested_quantity for req in active_requests)
        available_count = item.current_count - requested_total
        
        return {
            "id": item.id,
            "article": item.article,
            "nameRus": item.name_rus,
            "nameEng": item.name_eng,
            "currentCount": item.current_count,
            "minStock": item.min_stock,
            "availableCount": available_count,  # Доступное количество с учетом активных заявок
            "storageName": item.storage_name,
            "comment": item.comment,
            "pdfUrl": item.pdf_url,
            "unitMeasurement": getattr(item, 'unit_measurement', None) or "шт.",
            "createdAt": item.created_at.isoformat() if item.created_at else None,
            "updatedAt": item.updated_at.isoformat() if item.updated_at else None
        }
    finally:
        db.close()


@app.route("/api/inventory", methods=["GET"])
def get_inventory_items():
    """Получить все товары со склада ЗИП"""
    db = SessionLocal()
    try:
        items = db.query(models.InventoryItem).order_by(models.InventoryItem.article).all()
        return jsonify([inventory_item_to_dict(item) for item in items])
    finally:
        db.close()


@app.route("/api/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    """Получить конкретный товар со склада"""
    db = SessionLocal()
    try:
        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(inventory_item_to_dict(item))
    finally:
        db.close()


@app.route("/api/inventory", methods=["POST"])
def create_inventory_item():
    """Создать новый товар на складе"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Проверяем уникальность артикула
        existing = db.query(models.InventoryItem).filter(
            models.InventoryItem.article == data.get("article")
        ).first()
        
        if existing:
            return jsonify({"error": "Item with this article already exists"}), 400
        
        item = models.InventoryItem(
            article=data.get("article"),
            name_rus=data.get("nameRus"),
            name_eng=data.get("nameEng"),
            current_count=data.get("currentCount", 0),
            min_stock=data.get("minStock", 0),
            storage_name=data.get("storageName"),
            comment=data.get("comment"),
            pdf_url=data.get("pdfUrl")
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return jsonify(inventory_item_to_dict(item)), 201
    finally:
        db.close()


@app.route("/api/inventory/<int:item_id>", methods=["PUT"])
def update_inventory_item(item_id):
    """Обновить товар на складе"""
    db = SessionLocal()
    try:
        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        data = request.get_json()
        
        if "article" in data and data["article"] != item.article:
            # Проверяем уникальность нового артикула
            existing = db.query(models.InventoryItem).filter(
                models.InventoryItem.article == data["article"]
            ).first()
            if existing:
                return jsonify({"error": "Item with this article already exists"}), 400
            item.article = data["article"]
        
        if "nameRus" in data:
            item.name_rus = data["nameRus"]
        if "nameEng" in data:
            item.name_eng = data["nameEng"]
        if "currentCount" in data:
            item.current_count = data["currentCount"]
        if "minStock" in data:
            item.min_stock = data["minStock"]
        if "storageName" in data:
            item.storage_name = data["storageName"]
        if "comment" in data:
            item.comment = data["comment"]
        if "pdfUrl" in data:
            item.pdf_url = data["pdfUrl"]
        
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        return jsonify(inventory_item_to_dict(item))
    finally:
        db.close()


@app.route("/api/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    """Удалить товар со склада"""
    db = SessionLocal()
    try:
        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        db.delete(item)
        db.commit()
        return jsonify({"message": "Item deleted successfully"})
    finally:
        db.close()


@app.route("/api/inventory/check-low-stock", methods=["POST"])
def check_low_stock():
    """
    Проверить товары с критически низким запасом
    и автоматически создать заявки для пополнения
    """
    db = SessionLocal()
    try:
        items = db.query(models.InventoryItem).all()
        low_stock_items = []
        created_requests = []
        
        for item in items:
            # Рассчитываем доступное количество
            active_requests = db.query(models.InventoryRequest).filter(
                models.InventoryRequest.inventory_item_id == item.id,
                models.InventoryRequest.status.in_(["новая", "в_процессе"])
            ).all()
            requested_total = sum(req.requested_quantity for req in active_requests)
            available_count = item.current_count - requested_total
            
            # Если доступное количество ниже минимума
            if available_count < item.min_stock:
                low_stock_items.append({
                    "id": item.id,
                    "article": item.article,
                    "nameRus": item.name_rus,
                    "currentCount": item.current_count,
                    "minStock": item.min_stock,
                    "availableCount": available_count
                })
                
                # Создаём автоматическую заявку если её ещё нет
                existing_auto_request = db.query(models.InventoryRequest).filter(
                    models.InventoryRequest.inventory_item_id == item.id,
                    models.InventoryRequest.reason == "auto",
                    models.InventoryRequest.status.in_(["новая", "в_процессе"])
                ).first()
                
                if not existing_auto_request:
                    # Вычисляем необходимое количество для пополнения
                    quantity_to_order = item.min_stock - available_count
                    
                    auto_request = models.InventoryRequest(
                        inventory_item_id=item.id,
                        requested_quantity=quantity_to_order,
                        reason="auto",
                        status="новая",
                        created_by="system"
                    )
                    db.add(auto_request)
                    db.flush()  # Получить ID заявки

                    # Создаём оповещение
                    alert = models.InventoryAlert(
                        inventory_request_id=auto_request.id,
                        alert_type="warning",
                        event_type="auto_request_created",
                        message=f"Автоматическая заявка на пополнение запаса: {item.name_rus} ({item.article}) - {quantity_to_order} шт."
                    )
                    db.add(alert)
                    
                    created_requests.append({
                        "requestId": auto_request.id,
                        "itemId": item.id,
                        "itemArticle": item.article,
                        "quantity": quantity_to_order
                    })
        
        db.commit()
        
        return jsonify({
            "lowStockItems": low_stock_items,
            "createdAutoRequests": created_requests,
            "message": f"Found {len(low_stock_items)} items with low stock"
        })
    finally:
        db.close()


# ========== INVENTORY REQUESTS (ЗАЯВКИ НА ПОПОЛНЕНИЕ) ==========

def inventory_request_to_dict(req):
    """Преобразовать InventoryRequest в JSON"""
    item_data = {}
    if req.inventory_item:
        item_data = {
            "id": req.inventory_item.id,
            "article": req.inventory_item.article,
            "nameRus": req.inventory_item.name_rus,
            "nameEng": req.inventory_item.name_eng
        }
    
    return {
        "id": req.id,
        "inventoryItem": item_data,
        "requestedQuantity": req.requested_quantity,
        "reason": req.reason,  # manual | auto
        "status": req.status,  # новая|в_процессе|выполнена|отменена
        "relatedRepairDetailId": req.related_repair_detail_id,
        "relatedReportId": req.related_report_id,
        "createdBy": req.created_by,
        "notificationSent": req.notification_sent,
        "plannedDeliveryDate": req.planned_delivery_date,
        "actualDeliveryDate": req.actual_delivery_date,
        "createdAt": req.created_at.isoformat() if req.created_at else None,
        "updatedAt": req.updated_at.isoformat() if req.updated_at else None
    }


@app.route("/api/inventory-requests", methods=["GET"])
def get_inventory_requests():
    """Получить все заявки на пополнение запасов"""
    db = SessionLocal()
    try:
        # Можно добавить фильтр по статусу через параметры запроса
        status = request.args.get("status")
        
        query = db.query(models.InventoryRequest)
        if status:
            query = query.filter(models.InventoryRequest.status == status)
        
        requests = query.order_by(models.InventoryRequest.created_at.desc()).all()
        return jsonify([inventory_request_to_dict(req) for req in requests])
    finally:
        db.close()


@app.route("/api/inventory-requests/<int:request_id>", methods=["GET"])
def get_inventory_request(request_id):
    """Получить конкретную заявку"""
    db = SessionLocal()
    try:
        req = db.query(models.InventoryRequest).filter(models.InventoryRequest.id == request_id).first()
        if not req:
            return jsonify({"error": "Request not found"}), 404
        return jsonify(inventory_request_to_dict(req))
    finally:
        db.close()


@app.route("/api/inventory-requests", methods=["POST"])
def create_inventory_request():
    """Создать новую заявку на пополнение запасов"""
    db = SessionLocal()
    try:
        data = request.get_json()
        
        # Проверяем наличие товара
        item = db.query(models.InventoryItem).filter(
            models.InventoryItem.id == data.get("inventoryItemId")
        ).first()
        
        if not item:
            return jsonify({"error": "Inventory item not found"}), 404
        
        new_request = models.InventoryRequest(
            inventory_item_id=data.get("inventoryItemId"),
            requested_quantity=data.get("requestedQuantity"),
            reason=data.get("reason", "manual"),  # manual | auto
            status="новая",
            related_repair_detail_id=data.get("relatedRepairDetailId"),
            related_report_id=data.get("relatedReportId"),
            created_by=data.get("createdBy", "user"),
            planned_delivery_date=data.get("plannedDeliveryDate")
        )
        
        db.add(new_request)
        db.flush()  # Получить ID

        # if not message or not message.strip():
        #                 raise ValueError("Alert message cannot be empty")
        # Создаём уведомление
        alert = models.InventoryAlert(
            inventory_request_id=new_request.id,
            alert_type="info",
            event_type="new_request",
            message=f"Новая заявка на пополнение: {item.name_rus} ({item.article}) - {data.get('requestedQuantity')} шт."
        )
        db.add(alert)
        
        new_request.notification_sent = True
        
        db.commit()
        db.refresh(new_request)
        return jsonify(inventory_request_to_dict(new_request)), 201
    finally:
        db.close()


@app.route("/api/inventory-requests/<int:request_id>", methods=["PUT"])
def update_inventory_request(request_id):
    """Обновить заявку (изменить статус, дату и т.д.)"""
    db = SessionLocal()
    try:
        req = db.query(models.InventoryRequest).filter(
            models.InventoryRequest.id == request_id
        ).first()
        
        if not req:
            return jsonify({"error": "Request not found"}), 404
        
        data = request.get_json()
        
        old_status = req.status
        
        if "status" in data:
            req.status = data["status"]
            
            # При выполнении заявки обновляем количество товара (ПОПОЛНЕНИЕ!)
            if data["status"] == "выполнена" and old_status != "выполнена":
                item = req.inventory_item

                if item:
                    # ДОБАВЛЯЕМ количество товара на склад (это пополнение!)
                    item.current_count += req.requested_quantity
                    item.updated_at = datetime.utcnow()
                    
                    if not message or not message.strip():
                        raise ValueError("Alert message cannot be empty")
                    # Создаём оповещение о выполнении
                    alert = models.InventoryAlert(
                        inventory_request_id=req.id,
                        alert_type="success",
                        event_type="request_completed",
                        message=f"Заявка выполнена: {item.name_rus} ({item.article}) выдано {req.requested_quantity} шт."
                    )
                    db.add(alert)
        
        if "requestedQuantity" in data:
            req.requested_quantity = data["requestedQuantity"]
        if "plannedDeliveryDate" in data:
            req.planned_delivery_date = data["plannedDeliveryDate"]
        if "actualDeliveryDate" in data:
            req.actual_delivery_date = data["actualDeliveryDate"]
        if "createdBy" in data:
            req.created_by = data["createdBy"]
        
        req.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(req)
        return jsonify(inventory_request_to_dict(req))
    finally:
        db.close()


@app.route("/api/inventory-requests/<int:request_id>", methods=["DELETE"])
def delete_inventory_request(request_id):
    """Удалить/отменить заявку"""
    db = SessionLocal()
    try:
        req = db.query(models.InventoryRequest).filter(
            models.InventoryRequest.id == request_id
        ).first()
        
        if not req:
            return jsonify({"error": "Request not found"}), 404
        
        req.status = "отменена"
        db.commit()
        
        return jsonify({"message": "Request cancelled"})
    finally:
        db.close()


# ========== INVENTORY ALERTS (ОПОВЕЩЕНИЯ) ==========

def alert_to_dict(alert):
    """Преобразовать Alert в JSON"""
    return {
        "id": alert.id,
        "inventoryRequestId": alert.inventory_request_id,
        "alertType": alert.alert_type,  # info|warning|critical|success
        "eventType": alert.event_type,
        "message": alert.message,
        "isRead": alert.is_read,
        "createdAt": alert.created_at.isoformat() if alert.created_at else None
    }


@app.route("/api/inventory-alerts", methods=["GET"])
def get_inventory_alerts():
    """Получить все оповещения по запасам"""
    db = SessionLocal()
    try:
        # Можно добавить фильтры
        unread_only = request.args.get("unread", "false").lower() == "true"
        limit = int(request.args.get("limit", 50))
        
        query = db.query(models.InventoryAlert).order_by(models.InventoryAlert.created_at.desc())
        
        if unread_only:
            query = query.filter(models.InventoryAlert.is_read == False)
        
        alerts = query.limit(limit).all()
        alerts = sorted(alerts, key=lambda x: (x.is_read, -x.created_at.timestamp()))
        alerts = [a for a in alerts if a.message and a.message.strip()]
        return jsonify([alert_to_dict(alert) for alert in alerts])
    finally:
        db.close()


@app.route("/api/inventory-alerts/<int:alert_id>", methods=["PUT"])
def mark_alert_as_read(alert_id):
    """Отметить оповещение как прочитанное"""
    db = SessionLocal()
    try:
        alert = db.query(models.InventoryAlert).filter(
            models.InventoryAlert.id == alert_id
        ).first()
        
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        
        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return jsonify(alert_to_dict(alert))
    finally:
        db.close()


@app.route("/api/inventory-alerts/mark-all-read", methods=["POST"])
def mark_all_alerts_read():
    """Отметить все оповещения как прочитанные"""
    db = SessionLocal()
    try:
        db.query(models.InventoryAlert).filter(
            models.InventoryAlert.is_read == False
        ).update({models.InventoryAlert.is_read: True})
        db.commit()
        return jsonify({"message": "All alerts marked as read"})
    finally:
        db.close()


@app.route("/api/inventory-alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(alert_id):
    """Удалить оповещение"""
    db = SessionLocal()
    try:
        alert = db.query(models.InventoryAlert).filter(
            models.InventoryAlert.id == alert_id
        ).first()
        
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        
        db.delete(alert)
        db.commit()
        return jsonify({"message": "Alert deleted"})
    finally:
        db.close()


# ========== STATISTICS & ANALYTICS FOR INVENTORY ==========

@app.route("/api/inventory/stats/overview", methods=["GET"])
def inventory_stats():
    """Получить статистику по запасам"""
    db = SessionLocal()
    try:
        all_items = db.query(models.InventoryItem).all()
        
        low_stock_count = 0
        critical_stock_count = 0
        total_value_approx = 0
        
        for item in all_items:
            # Рассчитываем доступное
            active_requests = db.query(models.InventoryRequest).filter(
                models.InventoryRequest.inventory_item_id == item.id,
                models.InventoryRequest.status.in_(["новая", "в_процессе"])
            ).all()
            requested_total = sum(req.requested_quantity for req in active_requests)
            available = item.current_count - requested_total
            
            if available < item.min_stock:
                low_stock_count += 1
                if available <= 0:
                    critical_stock_count += 1
        
        # Получаем статистику по заявкам
        total_requests = db.query(models.InventoryRequest).count()
        new_requests = db.query(models.InventoryRequest).filter(
            models.InventoryRequest.status == "новая"
        ).count()
        
        unread_alerts = db.query(models.InventoryAlert).filter(
            models.InventoryAlert.is_read == False
        ).count()
        
        return jsonify({
            "totalItems": len(all_items),
            "lowStockCount": low_stock_count,
            "criticalStockCount": critical_stock_count,
            "totalRequests": total_requests,
            "newRequests": new_requests,
            "unreadAlerts": unread_alerts
        })
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
