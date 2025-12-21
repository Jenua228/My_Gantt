from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

