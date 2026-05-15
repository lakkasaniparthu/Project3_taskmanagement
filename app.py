import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from config import Config
from models import Project, Task, User, db


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PROJECT_STATUSES = ["Not Started", "In Progress", "Completed"]
TASK_PRIORITIES = ["Low", "Medium", "High"]
TASK_STATUSES = ["Not Started", "In Progress", "Completed"]


def validate_user_form(full_name, email, current_user_id=None):
    errors = []

    if not full_name:
        errors.append("Full name cannot be empty.")

    if not email:
        errors.append("Email cannot be empty.")
    elif not EMAIL_PATTERN.match(email):
        errors.append("Email should look like a valid email address.")

    if email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.user_id != current_user_id:
            errors.append("A user with this email already exists.")

    return errors


def parse_date(date_text):
    if not date_text:
        return None

    return datetime.strptime(date_text, "%Y-%m-%d").date()


def parse_hours(hours_text):
    if not hours_text:
        return Decimal("0")

    return Decimal(hours_text)


def validate_project_form(project_name, status, user_id, start_date, due_date):
    errors = []

    if not project_name:
        errors.append("Project name cannot be empty.")

    if status not in PROJECT_STATUSES:
        errors.append("Status must be Not Started, In Progress, or Completed.")

    if not user_id:
        errors.append("Each project must belong to a user.")
    elif not User.query.get(user_id):
        errors.append("Selected project owner does not exist.")

    if start_date and due_date and due_date < start_date:
        errors.append("Due date cannot be earlier than start date.")

    return errors


def validate_task_form(
    task_name,
    project_id,
    assigned_user_id,
    priority,
    status,
    estimated_hours,
    actual_hours,
    created_date,
    due_date,
):
    errors = []

    if not task_name:
        errors.append("Task name cannot be empty.")

    if not project_id:
        errors.append("Each task must belong to a project.")
    elif not Project.query.get(project_id):
        errors.append("Selected project does not exist.")

    if not assigned_user_id:
        errors.append("Each task must be assigned to a user.")
    elif not User.query.get(assigned_user_id):
        errors.append("Selected assigned user does not exist.")

    if priority not in TASK_PRIORITIES:
        errors.append("Priority must be Low, Medium, or High.")

    if status not in TASK_STATUSES:
        errors.append("Status must be Not Started, In Progress, or Completed.")

    if estimated_hours < 0:
        errors.append("Estimated hours cannot be negative.")

    if actual_hours < 0:
        errors.append("Actual hours cannot be negative.")

    if not created_date:
        errors.append("Created date is required.")

    if created_date and due_date and due_date < created_date:
        errors.append("Due date cannot be earlier than created date.")

    return errors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/users")
    def users_list():
        users = User.query.order_by(User.full_name).all()
        return render_template("users/list.html", users=users)

    @app.route("/users/new", methods=["GET", "POST"])
    def users_create():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            errors = validate_user_form(full_name, email)

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "users/form.html",
                    form_title="Add User",
                    user=None,
                    full_name=full_name,
                    email=email,
                )

            user = User(full_name=full_name, email=email)
            db.session.add(user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("A user with this email already exists.", "danger")
                return render_template(
                    "users/form.html",
                    form_title="Add User",
                    user=None,
                    full_name=full_name,
                    email=email,
                )

            flash("User added successfully.", "success")
            return redirect(url_for("users_detail", user_id=user.user_id))

        return render_template(
            "users/form.html",
            form_title="Add User",
            user=None,
            full_name="",
            email="",
        )

    @app.route("/users/<int:user_id>")
    def users_detail(user_id):
        user = User.query.get_or_404(user_id)
        return render_template("users/detail.html", user=user)

    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    def users_edit(user_id):
        user = User.query.get_or_404(user_id)

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            errors = validate_user_form(full_name, email, current_user_id=user.user_id)

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "users/form.html",
                    form_title="Edit User",
                    user=user,
                    full_name=full_name,
                    email=email,
                )

            user.full_name = full_name
            user.email = email

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("A user with this email already exists.", "danger")
                return render_template(
                    "users/form.html",
                    form_title="Edit User",
                    user=user,
                    full_name=full_name,
                    email=email,
                )

            flash("User updated successfully.", "success")
            return redirect(url_for("users_detail", user_id=user.user_id))

        return render_template(
            "users/form.html",
            form_title="Edit User",
            user=user,
            full_name=user.full_name,
            email=user.email,
        )

    @app.route("/users/<int:user_id>/delete", methods=["POST"])
    def users_delete(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
        return redirect(url_for("users_list"))

    @app.route("/projects")
    def projects_list():
        projects = Project.query.order_by(Project.due_date, Project.project_name).all()
        return render_template("projects/list.html", projects=projects)

    @app.route("/projects/new", methods=["GET", "POST"])
    def projects_create():
        users = User.query.order_by(User.full_name).all()

        if not users:
            flash("Add a user before creating a project.", "warning")
            return redirect(url_for("users_create"))

        if request.method == "POST":
            project_name = request.form.get("project_name", "").strip()
            status = request.form.get("status", "")
            user_id = request.form.get("user_id", type=int)
            start_date_text = request.form.get("start_date", "")
            due_date_text = request.form.get("due_date", "")

            try:
                start_date = parse_date(start_date_text)
                due_date = parse_date(due_date_text)
                errors = validate_project_form(
                    project_name,
                    status,
                    user_id,
                    start_date,
                    due_date,
                )
            except ValueError:
                start_date = None
                due_date = None
                errors = ["Dates must use the YYYY-MM-DD format."]

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "projects/form.html",
                    form_title="Add Project",
                    project=None,
                    users=users,
                    statuses=PROJECT_STATUSES,
                    project_name=project_name,
                    status=status,
                    user_id=user_id,
                    start_date=start_date_text,
                    due_date=due_date_text,
                )

            project = Project(
                project_name=project_name,
                status=status,
                user_id=user_id,
                start_date=start_date,
                due_date=due_date,
            )
            db.session.add(project)
            db.session.commit()

            flash("Project added successfully.", "success")
            return redirect(url_for("projects_detail", project_id=project.project_id))

        return render_template(
            "projects/form.html",
            form_title="Add Project",
            project=None,
            users=users,
            statuses=PROJECT_STATUSES,
            project_name="",
            status="Not Started",
            user_id=users[0].user_id,
            start_date="",
            due_date="",
        )

    @app.route("/projects/<int:project_id>")
    def projects_detail(project_id):
        project = Project.query.get_or_404(project_id)
        return render_template("projects/detail.html", project=project)

    @app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
    def projects_edit(project_id):
        project = Project.query.get_or_404(project_id)
        users = User.query.order_by(User.full_name).all()

        if not users:
            flash("Add a user before editing projects.", "warning")
            return redirect(url_for("users_create"))

        if request.method == "POST":
            project_name = request.form.get("project_name", "").strip()
            status = request.form.get("status", "")
            user_id = request.form.get("user_id", type=int)
            start_date_text = request.form.get("start_date", "")
            due_date_text = request.form.get("due_date", "")

            try:
                start_date = parse_date(start_date_text)
                due_date = parse_date(due_date_text)
                errors = validate_project_form(
                    project_name,
                    status,
                    user_id,
                    start_date,
                    due_date,
                )
            except ValueError:
                start_date = None
                due_date = None
                errors = ["Dates must use the YYYY-MM-DD format."]

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "projects/form.html",
                    form_title="Edit Project",
                    project=project,
                    users=users,
                    statuses=PROJECT_STATUSES,
                    project_name=project_name,
                    status=status,
                    user_id=user_id,
                    start_date=start_date_text,
                    due_date=due_date_text,
                )

            project.project_name = project_name
            project.status = status
            project.user_id = user_id
            project.start_date = start_date
            project.due_date = due_date
            db.session.commit()

            flash("Project updated successfully.", "success")
            return redirect(url_for("projects_detail", project_id=project.project_id))

        return render_template(
            "projects/form.html",
            form_title="Edit Project",
            project=project,
            users=users,
            statuses=PROJECT_STATUSES,
            project_name=project.project_name,
            status=project.status,
            user_id=project.user_id,
            start_date=project.start_date.isoformat() if project.start_date else "",
            due_date=project.due_date.isoformat() if project.due_date else "",
        )

    @app.route("/projects/<int:project_id>/delete", methods=["POST"])
    def projects_delete(project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted successfully.", "success")
        return redirect(url_for("projects_list"))

    @app.route("/tasks")
    def tasks_list():
        tasks = Task.query.order_by(Task.due_date, Task.task_name).all()
        return render_template("tasks/list.html", tasks=tasks)

    @app.route("/tasks/new", methods=["GET", "POST"])
    def tasks_create():
        projects = Project.query.order_by(Project.project_name).all()
        users = User.query.order_by(User.full_name).all()

        if not projects:
            flash("Add a project before creating a task.", "warning")
            return redirect(url_for("projects_create"))

        if not users:
            flash("Add a user before creating a task.", "warning")
            return redirect(url_for("users_create"))

        if request.method == "POST":
            task_name = request.form.get("task_name", "").strip()
            project_id = request.form.get("project_id", type=int)
            assigned_user_id = request.form.get("assigned_user_id", type=int)
            priority = request.form.get("priority", "")
            status = request.form.get("status", "")
            estimated_hours_text = request.form.get("estimated_hours", "")
            actual_hours_text = request.form.get("actual_hours", "")
            created_date_text = request.form.get("created_date", "")
            due_date_text = request.form.get("due_date", "")

            try:
                estimated_hours = parse_hours(estimated_hours_text)
                actual_hours = parse_hours(actual_hours_text)
                created_date = parse_date(created_date_text)
                due_date = parse_date(due_date_text)
                errors = validate_task_form(
                    task_name,
                    project_id,
                    assigned_user_id,
                    priority,
                    status,
                    estimated_hours,
                    actual_hours,
                    created_date,
                    due_date,
                )
            except (InvalidOperation, ValueError):
                estimated_hours = Decimal("0")
                actual_hours = Decimal("0")
                created_date = None
                due_date = None
                errors = ["Hours must be valid numbers and dates must use the YYYY-MM-DD format."]

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "tasks/form.html",
                    form_title="Add Task",
                    task=None,
                    projects=projects,
                    users=users,
                    priorities=TASK_PRIORITIES,
                    statuses=TASK_STATUSES,
                    task_name=task_name,
                    project_id=project_id,
                    assigned_user_id=assigned_user_id,
                    priority=priority,
                    status=status,
                    estimated_hours=estimated_hours_text,
                    actual_hours=actual_hours_text,
                    created_date=created_date_text,
                    due_date=due_date_text,
                )

            task = Task(
                task_name=task_name,
                project_id=project_id,
                assigned_user_id=assigned_user_id,
                priority=priority,
                status=status,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours,
                created_date=created_date,
                due_date=due_date,
            )
            db.session.add(task)
            db.session.commit()

            flash("Task added successfully.", "success")
            return redirect(url_for("tasks_detail", task_id=task.task_id))

        today = datetime.today().date().isoformat()
        return render_template(
            "tasks/form.html",
            form_title="Add Task",
            task=None,
            projects=projects,
            users=users,
            priorities=TASK_PRIORITIES,
            statuses=TASK_STATUSES,
            task_name="",
            project_id=projects[0].project_id,
            assigned_user_id=users[0].user_id,
            priority="Medium",
            status="Not Started",
            estimated_hours="0",
            actual_hours="0",
            created_date=today,
            due_date="",
        )

    @app.route("/tasks/<int:task_id>")
    def tasks_detail(task_id):
        task = Task.query.get_or_404(task_id)
        return render_template("tasks/detail.html", task=task)

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    def tasks_edit(task_id):
        task = Task.query.get_or_404(task_id)
        projects = Project.query.order_by(Project.project_name).all()
        users = User.query.order_by(User.full_name).all()

        if not projects:
            flash("Add a project before editing tasks.", "warning")
            return redirect(url_for("projects_create"))

        if not users:
            flash("Add a user before editing tasks.", "warning")
            return redirect(url_for("users_create"))

        if request.method == "POST":
            task_name = request.form.get("task_name", "").strip()
            project_id = request.form.get("project_id", type=int)
            assigned_user_id = request.form.get("assigned_user_id", type=int)
            priority = request.form.get("priority", "")
            status = request.form.get("status", "")
            estimated_hours_text = request.form.get("estimated_hours", "")
            actual_hours_text = request.form.get("actual_hours", "")
            created_date_text = request.form.get("created_date", "")
            due_date_text = request.form.get("due_date", "")

            try:
                estimated_hours = parse_hours(estimated_hours_text)
                actual_hours = parse_hours(actual_hours_text)
                created_date = parse_date(created_date_text)
                due_date = parse_date(due_date_text)
                errors = validate_task_form(
                    task_name,
                    project_id,
                    assigned_user_id,
                    priority,
                    status,
                    estimated_hours,
                    actual_hours,
                    created_date,
                    due_date,
                )
            except (InvalidOperation, ValueError):
                estimated_hours = Decimal("0")
                actual_hours = Decimal("0")
                created_date = None
                due_date = None
                errors = ["Hours must be valid numbers and dates must use the YYYY-MM-DD format."]

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template(
                    "tasks/form.html",
                    form_title="Edit Task",
                    task=task,
                    projects=projects,
                    users=users,
                    priorities=TASK_PRIORITIES,
                    statuses=TASK_STATUSES,
                    task_name=task_name,
                    project_id=project_id,
                    assigned_user_id=assigned_user_id,
                    priority=priority,
                    status=status,
                    estimated_hours=estimated_hours_text,
                    actual_hours=actual_hours_text,
                    created_date=created_date_text,
                    due_date=due_date_text,
                )

            task.task_name = task_name
            task.project_id = project_id
            task.assigned_user_id = assigned_user_id
            task.priority = priority
            task.status = status
            task.estimated_hours = estimated_hours
            task.actual_hours = actual_hours
            task.created_date = created_date
            task.due_date = due_date
            db.session.commit()

            flash("Task updated successfully.", "success")
            return redirect(url_for("tasks_detail", task_id=task.task_id))

        return render_template(
            "tasks/form.html",
            form_title="Edit Task",
            task=task,
            projects=projects,
            users=users,
            priorities=TASK_PRIORITIES,
            statuses=TASK_STATUSES,
            task_name=task.task_name,
            project_id=task.project_id,
            assigned_user_id=task.assigned_user_id,
            priority=task.priority,
            status=task.status,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            created_date=task.created_date.isoformat() if task.created_date else "",
            due_date=task.due_date.isoformat() if task.due_date else "",
        )

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    def tasks_delete(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully.", "success")
        return redirect(url_for("tasks_list"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
