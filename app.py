import re

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from config import Config
from models import User, db


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
