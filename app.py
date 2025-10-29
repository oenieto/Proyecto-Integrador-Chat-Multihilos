from flask import Flask, render_template

# Indicar a Flask que la carpeta de archivos estáticos se llama 'statics'
app = Flask(__name__, static_folder='statics')

@app.route('/')
def index():
    # Ahora que index.html está en 'templates', usamos render_template
    return render_template('index.html')

# Si necesitas rutas adicionales, las agregarías aquí, por ejemplo:
# @app.route('/api/messages', methods=['GET', 'POST'])
# def messages():
#     # Lógica para API de mensajes
#     pass

# El if __name__ == '__main__': lo habíamos quitado, pero si lo necesitas
# para ejecutar directamente desde el script, lo podrías reponer así:
# if __name__ == '__main__':
#     app.run(debug=True)