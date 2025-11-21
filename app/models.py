from datetime import datetime
from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_url = db.Column(db.String(255), default="")

    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)


    def avatar(self, size=100):
        """Genera un avatar con las iniciales del usuario."""
        # Usamos el color morado de tu burbuja de chat
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&size={size}&background=5B4DA8&color=FFFFFF"



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    # ... (después de name = db.Column...) ...

    def room_avatar(self, size=100):
        """Genera un avatar con las iniciales del nombre de la sala."""
        # Usamos un gris oscuro para diferenciarlo
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&size={size}&background=2a2a2e&color=FFFFFF"

# ... (la clase Message empieza aquí) ...

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    room = db.relationship('Room', backref=db.backref('messages', lazy=True))
    user = db.relationship('User')
