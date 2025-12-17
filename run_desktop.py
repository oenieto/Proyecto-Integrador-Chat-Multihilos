import webview
import sys
import threading
import time
from app import create_app, socketio

# Configuración
PORT = 5000
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"

def start_server():
    # Creamos la app igual que en app.py
    app = create_app(use_statics_folder=False)
    # Importante: debug=False y use_reloader=False para evitar problemas de hilos
    socketio.run(app, host=HOST, port=PORT, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    print(f"Iniciando servidor en {URL}...")
    # Iniciar servidor Flask-SocketIO en un hilo separado
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # Esperar un poco a que el servidor arranque
    time.sleep(2)

    # Crear la ventana nativa
    webview.create_window('Wavvi - Tu Chat', URL, width=1200, height=800, resizable=True)
    
    # Iniciar el loop de la interfaz gráfica
    print("Iniciando ventana...")
    webview.start()
    
    print("Cerrando aplicación...")
    sys.exit()
