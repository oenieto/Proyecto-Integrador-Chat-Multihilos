from flask import render_template
from flask_login import login_required, current_user
from . import main_bp
from ..models import Room, Message

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
    msgs = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.asc()).all()
    return render_template("chat.html", room=room, messages=msgs, me=current_user)

@main_bp.get("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")
