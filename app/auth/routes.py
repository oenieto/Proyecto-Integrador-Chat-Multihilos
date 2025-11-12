from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from ..models import db, User


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        # Si ya está logueado, lo mandamos a los chats
        return redirect(url_for("main.chats")) 
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
    # --- CAMBIO 1 ---
    # Redirigir a la lista de chats, no al index
    return redirect(url_for("main.chats")) 


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
    
    # --- CAMBIO 2 (Opción B) ---
    # No iniciamos sesión automáticamente
    # login_user(user) 
    
    # Redirigimos al login para que inicie sesión
    return redirect(url_for("auth.login"))


@auth_bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))