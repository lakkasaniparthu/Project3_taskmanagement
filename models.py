from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    projects = db.relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    assigned_tasks = db.relationship(
        "Task",
        back_populates="assigned_user",
        foreign_keys="Task.assigned_user_id",
    )

    def __repr__(self):
        return f"<User {self.full_name}>"


class Project(db.Model):
    __tablename__ = "projects"

    project_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    project_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Planning")
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    owner = db.relationship("User", back_populates="projects")
    tasks = db.relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Project {self.project_name}>"


class Task(db.Model):
    __tablename__ = "tasks"

    task_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id"), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    task_name = db.Column(db.String(150), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(30), nullable=False, default="To Do")
    estimated_hours = db.Column(db.Numeric(6, 2), nullable=False, default=0)
    actual_hours = db.Column(db.Numeric(6, 2), nullable=False, default=0)
    created_date = db.Column(db.Date, nullable=False, server_default=db.text("(CURRENT_DATE)"))
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    project = db.relationship("Project", back_populates="tasks")
    assigned_user = db.relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_user_id],
    )

    def __repr__(self):
        return f"<Task {self.task_name}>"
