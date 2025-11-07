# app.py
from app import create_app, socketio

# Si dejaste la carpeta 'static' renombrada correctamente:
app = create_app(use_statics_folder=True)

# Si quieres mantener 'statics/':
# app = create_app(use_statics_folder=True)

if __name__ == "__main__":
    # eventlet para websockets estables
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
