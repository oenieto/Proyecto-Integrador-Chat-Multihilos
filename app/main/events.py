from datetime import datetime
from flask_socketio import join_room, emit
from flask_login import current_user
from ..models import db, Message, Room, MessageReaction

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
        # emit("system", {"msg": f"{current_user.name} se unió"}, to=str(room_id)) # Opcional: ruido visual

    @socketio.on("message")
    def on_message(data):
        room_id = int(data["room_id"])
        parent_id = data.get("parent_id") 
        body = (data.get("body") or "").strip()
        
        if not body:
            return

        # --- FILTRO DE GROSERÍAS ---
        bad_words = [
            "mierda", "puta", "puto", "cabron", "cabrón", "joder", "estupido", "estúpido",
            "idiota", "imbecil", "imbécil", "pendejo", "verga", "chinga", "marica", "maricon",
            "zorra", "maldito", "coño", "perra"
        ]
        
        # Usamos regex para reemplazo "case-insensitive"
        import re
        for bad in bad_words:
            # \b asegura que coincida palabra completa (evita censurar "computadora" por "puta")
            # Aunque si el usuario escribe "computadoraaa" no funcionará \b, así que lo dejamos simple por ahora o \b
            # Simplicidad: reemplazamos ocurrencias directas.
            pattern = re.compile(re.escape(bad), re.IGNORECASE)
            body = pattern.sub("*" * len(bad), body)
        # ---------------------------

        msg = Message(
            room_id=room_id, 
            user_id=current_user.id, 
            body=body,
            parent_id=parent_id if parent_id else None
        )
        db.session.add(msg)
        db.session.commit()
        
        emit("message", msg.to_dict(), to=str(room_id))

    @socketio.on("delete_message")
    def on_delete_message(data):
        msg_id = data.get("message_id")
        msg = Message.query.get(msg_id)
        
        if msg and msg.user_id == current_user.id:
            msg.is_deleted = True
            msg.deleted_at = datetime.utcnow()
            db.session.commit()
            
            # Emitimos evento de actualización
            emit("message_updated", msg.to_dict(), to=str(msg.room_id))

    @socketio.on("react_message")
    def on_react_message(data):
        msg_id = data.get("message_id")
        emoji = data.get("emoji")
        
        msg = Message.query.get(msg_id)
        if not msg:
            return

        # Verificar si ya existe reacción de este usuario en este mensaje y emoji
        existing = MessageReaction.query.filter_by(
            message_id=msg_id, user_id=current_user.id, emoji=emoji
        ).first()

        if existing:
            db.session.delete(existing) # Toggle OFF
        else:
            # Límites opcionales: solo 1 reacción por usuario por mensaje? No, dejemos múltiples.
            reaction = MessageReaction(message_id=msg_id, user_id=current_user.id, emoji=emoji)
            db.session.add(reaction)
        
        db.session.commit()
        
        # Emitimos actualización solo de este mensaje
        emit("message_updated", msg.to_dict(), to=str(msg.room_id))

    # --- Pizarra Compartida (Whiteboard) ---
    @socketio.on("draw")
    def on_draw(data):
        room_id = data.get("room_id")
        # Re-emitir a todos en la sala EXCEPTO al remitente (para fluidez local)
        emit("draw", data, to=str(room_id), include_self=False)

    @socketio.on("clear_board")
    def on_clear_board(data):
        room_id = data.get("room_id")
        emit("clear_board", {}, to=str(room_id))