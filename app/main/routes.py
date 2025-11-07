from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import main_bp
from ..models import Room, Message, db

@main_bp.get("/")
@login_required
def index():
    rooms = Room.query.order_by(Room.name.asc()).all()
    return render_template("index.html", rooms=rooms)

@main_bp.get("/chats")
@login_required
def chats():
    rooms = Room.query.order_by(Room.name.asc()).all()
    return render_template("chats.html", rooms=rooms)

@main_bp.get("/chat/<int:room_id>")
@login_required
def chat(room_id):
    room = Room.query.get_or_404(room_id)
    rooms = Room.query.order_by(Room.name.asc()).all()  # <- para la lista izquierda
    msgs = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.asc()).all()
    return render_template("chat.html", room=room, rooms=rooms, messages=msgs, me=current_user)
# NUEVO: crear sala y redirigir
@main_bp.post("/rooms/new")
@login_required
def create_room():
    name = (request.form.get("room_name") or "").strip()
    if not name:
        flash("Ponle un nombre a la conversación", "error")
        return redirect(url_for("main.chats"))
    room = Room.query.filter(db.func.lower(Room.name) == name.lower()).first()
    if not room:
        room = Room(name=name)
        db.session.add(room)
        db.session.commit()
    return redirect(url_for("main.chat", room_id=room.id))

@main_bp.get("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")
