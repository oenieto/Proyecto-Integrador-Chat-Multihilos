from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
login_manager = LoginManager()
# threading: funciona bien en Windows sin instalar eventlet
socketio = SocketIO(async_mode="threading")

def create_app(test_config=None, use_statics_folder=False):
    static_folder = "statics" if use_statics_folder else "static"
    app = Flask(__name__, instance_relative_config=True,
                static_folder=static_folder, template_folder="templates")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-key"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "chat.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, static_folder, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024 # 16 MB max limit
    )

    # Crear carpeta de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    socketio.init_app(app)

    # Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Eventos Socket.IO
    from .main.events import register_socketio_handlers
    register_socketio_handlers(socketio)

    # Crear tablas
    with app.app_context():
        db.create_all()

    return app
