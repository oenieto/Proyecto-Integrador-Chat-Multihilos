from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from . import main_bp
from ..models import Room, Message, db, User
from werkzeug.utils import secure_filename
import os

@main_bp.get("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.chats'))
    return render_template("index.html")

@main_bp.get("/chats")
@login_required
def chats():
    # 1. Busca salas donde soy participante
    room = current_user.rooms.filter_by(is_private=False).first()
    
    if room:
        return redirect(url_for('main.chat', room_id=room.id))
    
    # 2. Si no estoy en ninguna, busca la General o crea una
    general = Room.query.filter_by(name="General").first()
    if not general:
        general = Room(name="General", is_private=False)
        db.session.add(general)
        db.session.commit()
    
    if current_user not in general.participants:
        general.participants.append(current_user)
        db.session.commit()
        
    return redirect(url_for('main.chat', room_id=general.id))

@main_bp.get("/chat/<int:room_id>")
@login_required
def chat(room_id):
    room = Room.query.get_or_404(room_id)
    
    # Separar salas públicas y privadas (solo las que participo)
    public_rooms = current_user.rooms.filter_by(is_private=False).order_by(Room.name.asc()).all()
    private_rooms = current_user.rooms.filter_by(is_private=True).all()
    
    # Si la sala actual no está en mis salas (ej. url directa), unirme si es pública
    if not room.is_private and current_user not in room.participants:
        room.participants.append(current_user)
        db.session.commit()
        # Recargar listas
        public_rooms = current_user.rooms.filter_by(is_private=False).order_by(Room.name.asc()).all()

    msgs = Message.query.filter_by(room_id=room.id).order_by(Message.created_at.asc()).all()
    users = User.query.filter(User.id != current_user.id).all()
    
    return render_template("chat.html", room=room, public_rooms=public_rooms, private_rooms=private_rooms, messages=msgs, me=current_user, users=users)

@main_bp.post("/rooms/new")
@login_required
def create_room():
    name = (request.form.get("room_name") or "").strip()
    participant_ids = request.form.getlist("participants")
    avatar_url = request.form.get("avatar_url") # Opción por URL (para GIFs)
    
    if not name:
        flash("Ponle un nombre a la conversación", "error")
        return redirect(url_for("main.chats"))
    
    new_room = Room(name=name, is_private=False)
    if avatar_url:
        new_room.avatar_url = avatar_url
        
    db.session.add(new_room)
    
    if current_user not in new_room.participants:
        new_room.participants.append(current_user)
        
    for uid in participant_ids:
        try:
            user = User.query.get(int(uid))
            if user and user not in new_room.participants:
                new_room.participants.append(user)
        except:
            pass
            
    db.session.commit()
    return redirect(url_for("main.chat", room_id=new_room.id))

@main_bp.post("/chat/<int:room_id>/delete")
@login_required
def delete_chat(room_id):
    room = Room.query.get_or_404(room_id)
    if current_user in room.participants:
        room.participants.remove(current_user)
        db.session.commit()
    return redirect(url_for('main.chats'))

@main_bp.get("/chat/private/<int:user_id>")
@login_required
def start_private_chat(user_id):
    other_user = User.query.get_or_404(user_id)
    existing_room = None
    for room in current_user.rooms:
        if room.is_private and other_user in room.participants:
            existing_room = room
            break
            
    if existing_room:
        return redirect(url_for("main.chat", room_id=existing_room.id))
        
    room_name = f"private_{min(current_user.id, other_user.id)}_{max(current_user.id, other_user.id)}"
    new_room = Room(name=room_name, is_private=True)
    new_room.participants.append(current_user)
    new_room.participants.append(other_user)
    db.session.add(new_room)
    db.session.commit()
    return redirect(url_for("main.chat", room_id=new_room.id))

@main_bp.get("/search")
@login_required
def search_users():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    users = User.query.filter(
        (User.name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%")),
        User.id != current_user.id
    ).limit(10).all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email, "avatar": u.avatar(50)} for u in users])

@main_bp.get("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                current_user.avatar_url = f"/static/uploads/{filename}"
        
        phone = request.form.get('phone_number')
        code = request.form.get('country_code')
        if phone: current_user.phone_number = phone
        if code: current_user.country_code = code
            
        db.session.commit()
        flash("Configuración actualizada", "success")
        return redirect(url_for('main.settings'))
        
    return render_template("settings.html")