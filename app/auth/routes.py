from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from ..models import db, User

@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash("Credenciales inválidas", "error")
        return redirect(url_for("auth.login"))
    login_user(user)
    return redirect(url_for("main.index"))

@auth_bp.get("/register")
def register():
    return render_template("register.html")

@auth_bp.post("/register")
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if User.query.filter_by(email=email).first():
        flash("Ese correo ya está registrado", "error")
        return redirect(url_for("auth.register"))
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for("main.index"))

@auth_bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
