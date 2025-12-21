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


def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "start_date": task.start_date.isoformat() if task.start_date else None,
        "end_date": task.end_date.isoformat() if task.end_date else None,
        "progress": task.progress,
        "color": task.color,
        "row_index": task.row_index,
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
            progress=data.get("progress", 0),
            color=data.get("color", "#4A90D9"),
            row_index=data.get("row_index", 0)
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
        if "progress" in data:
            db_task.progress = data["progress"]
        if "color" in data:
            db_task.color = data["color"]
        if "row_index" in data:
            db_task.row_index = data["row_index"]
        
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
        
        # Create demo tasks
        tasks = [
            models.Task(
                title="Project Planning",
                description="Initial project planning and requirements gathering",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 15),
                progress=100,
                color="#4CAF50",
                row_index=0
            ),
            models.Task(
                title="Design Phase",
                description="UI/UX design and architecture",
                start_date=datetime(2024, 1, 16),
                end_date=datetime(2024, 2, 5),
                progress=75,
                color="#2196F3",
                row_index=1
            ),
            models.Task(
                title="Backend Development",
                description="API and database development",
                start_date=datetime(2024, 2, 1),
                end_date=datetime(2024, 3, 15),
                progress=50,
                color="#9C27B0",
                row_index=2
            ),
            models.Task(
                title="Frontend Development",
                description="Vue.js frontend implementation",
                start_date=datetime(2024, 2, 10),
                end_date=datetime(2024, 3, 20),
                progress=30,
                color="#FF9800",
                row_index=3
            ),
            models.Task(
                title="Testing",
                description="Unit and integration testing",
                start_date=datetime(2024, 3, 15),
                end_date=datetime(2024, 4, 1),
                progress=0,
                color="#F44336",
                row_index=4
            ),
            models.Task(
                title="Deployment",
                description="Production deployment and launch",
                start_date=datetime(2024, 4, 1),
                end_date=datetime(2024, 4, 10),
                progress=0,
                color="#607D8B",
                row_index=5
            ),
        ]
        
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
            "tasks_created": len(tasks),
            "connections_created": len(connections)
        })
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
