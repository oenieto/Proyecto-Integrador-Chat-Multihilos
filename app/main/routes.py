from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import main_bp
from ..models import Room, Message, db

@main_bp.get("/")
def index():
    if current_user.is_authenticated:
        # Si ya está logueado, no mostramos la bienvenida, lo mandamos a los chats.
        return redirect(url_for('main.chats'))
    
    # Si no está logueado, le mostramos la nueva página de aterrizaje.
    return render_template("index.html")

# (La siguiente ruta, "@main_bp.get("/chats")", empieza aquí)

@main_bp.get("/chats")
@login_required
def chats():
    # Esta ruta ahora es un "redirigidor inteligente"
    
    # 1. Busca la primera sala pública disponible
    room = Room.query.filter_by(is_private=False).order_by(Room.name.asc()).first()
    
    if room:
        # 2. Si existe al menos una, te manda a esa.
        return redirect(url_for('main.chat', room_id=room.id))
    else:
        # 3. Si no hay NINGUNA sala, crea una "General" para que no te atores.
        general_room = Room(name="General", is_private=False)
        db.session.add(general_room)
        db.session.commit()
        # Y te manda a la sala que acaba de crear
        return redirect(url_for('main.chat', room_id=general_room.id))

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

@main_bp.get("/settings")
@login_required
def settings():
    return render_template("settings.html")