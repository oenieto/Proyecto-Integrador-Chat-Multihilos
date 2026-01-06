from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Tabla de asociación para chats privados (Many-to-Many)
room_participants = db.Table('room_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_url = db.Column(db.String(255), default="")
    phone_number = db.Column(db.String(20), nullable=True)
    country_code = db.Column(db.String(5), nullable=True)

    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)


    def avatar(self, size=100):
        """Genera un avatar con las iniciales del usuario."""
        if self.avatar_url:
            return self.avatar_url
        # Usamos el color morado de tu burbuja de chat
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&size={size}&background=5B4DA8&color=FFFFFF"



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    
    # Relación con usuarios (participantes)
    participants = db.relationship('User', secondary=room_participants, backref=db.backref('rooms', lazy='dynamic'))

    # ... (después de name = db.Column...) ...

    def room_avatar(self, size=100):
        """Genera un avatar con las iniciales del nombre de la sala."""
        if self.avatar_url:
            return self.avatar_url
        # Usamos un gris oscuro para diferenciarlo
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&size={size}&background=2a2a2e&color=FFFFFF"

    def display_name(self, viewer):
        """Devuelve el nombre a mostrar. Si es privado, devuelve el nombre del OTRO participante."""
        if not self.is_private:
            return self.name
        
        # Buscar el otro participante
        for p in self.participants:
            if p.id != viewer.id:
                return p.name
        
        return "Chat Privado" # Fallback por si acaso

# ... (la clase Message empieza aquí) ...

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Phase 1: Nuevas Funcionalidades ---
    # Respuestas (Hilos)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=True)
    replies = db.relationship('Message', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    # Eliminación lógica (Soft Delete)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones existentes
    room = db.relationship('Room', backref=db.backref('messages', lazy=True))
    user = db.relationship('User')

    def to_dict(self):
        """Helper para serializar el mensaje a JSON"""
        return {
            'id': self.id,
            'user': self.user.name,
            'user_id': self.user.id,
            'avatar': self.user.avatar(50),
            'body': "🚫 Este mensaje fue eliminado" if self.is_deleted else self.body,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.strftime("%H:%M"),
            'timestamp': self.created_at.isoformat(),
            'parent_id': self.parent_id,
            'parent_body': self.parent.body[:50] + "..." if self.parent and not self.parent.is_deleted else None,
            'parent_user': self.parent.user.name if self.parent else None,
            'reactions': {r.emoji: [u.user.name for u in self.reactions if u.emoji == r.emoji] for r in self.reactions} 
            # Nota: La serialización de reacciones puede optimizarse, esto es básico.
        }

class MessageReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emoji = db.Column(db.String(10), nullable=False) # 👍, ❤️, 😂, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    message = db.relationship('Message', backref=db.backref('reactions', lazy=True))

class Whiteboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False, default="Sin Título")
    image_url = db.Column(db.String(255), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    room = db.relationship('Room', backref=db.backref('whiteboards', lazy='dynamic'))
