# app/main/events.py
from flask_socketio import join_room, emit
from flask_login import current_user
from ..models import db, Message, Room

def register_socketio_handlers(socketio):
    @socketio.on("join")
    def on_join(data):
        room_id = int(data["room_id"])
        room = Room.query.get(room_id)
        
        # Seguridad: Si es privada, verificar que el usuario esté en la lista
        if room and room.is_private:
            if current_user not in room.participants:
                return # Rechazar conexión silenciosamente o manejar error
        
        join_room(str(room_id))
        emit("system", {"msg": f"{current_user.name} se unió"}, to=str(room_id))

    @socketio.on("message")
    def on_message(data):
        room_id = int(data["room_id"])
        body = (data.get("body") or "").strip()
        if not body:
            return
        msg = Message(room_id=room_id, user_id=current_user.id, body=body)
        db.session.add(msg)
        db.session.commit()
        emit("message", {
            "user_id": current_user.id,   # <-- añadido
            "user": current_user.name,
            "body": msg.body,
            "ts": msg.created_at.isoformat()
        }, to=str(room_id))