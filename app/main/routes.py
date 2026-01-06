from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from . import main_bp
from ..models import Room, Message, db, User, Whiteboard
from werkzeug.utils import secure_filename
import os
import time

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

@main_bp.post("/upload")
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(f"{current_user.id}_{int(time.time())}_{file.filename}") # Timestamp para unicidad
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({"url": url})
    return jsonify({"error": "Upload failed"}), 500

@main_bp.route('/save_whiteboard', methods=['POST'])
@login_required
def save_whiteboard():
    room_id = request.form.get('room_id')
    image_data = request.form.get('image') # Base64 string
    name = request.form.get('name', 'Sin Título')
    
    if not room_id or not image_data:
        return jsonify({'error': 'Missing data'}), 400

    import base64
    try:
        header, encoded = image_data.split(",", 1)
        file_ext = header.split(';')[0].split('/')[1]
        data = base64.b64decode(encoded)
        
        filename = f"wb_{room_id}_{int(time.time())}.{file_ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'whiteboards')
        os.makedirs(filepath, exist_ok=True)
        
        with open(os.path.join(filepath, filename), "wb") as f:
            f.write(data)
            
        url = url_for('static', filename=f'uploads/whiteboards/{filename}')
        
        wb = Whiteboard(room_id=room_id, image_url=url, name=name)
        db.session.add(wb)
        db.session.commit()
        
        return jsonify({'url': url, 'id': wb.id, 'name': wb.name})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to save'}), 500

@main_bp.route('/whiteboards/<int:room_id>')
@login_required
def get_whiteboards(room_id):
    wbs = Whiteboard.query.filter_by(room_id=room_id).order_by(Whiteboard.created_at.desc()).all()
    return jsonify([{
        'id': w.id,
        'url': w.image_url,
        'name': w.name,
        'created_at': w.created_at.strftime("%d/%m %H:%M")
    } for w in wbs])

@main_bp.route('/summarize/<int:room_id>')
@login_required
def summarize_chat(room_id):
    from app.models import Message
    
    # 1. Obtener últimos 50 mensajes
    messages = Message.query.filter_by(room_id=room_id, is_deleted=False)\
        .order_by(Message.created_at.desc()).limit(50).all()
        
    if not messages:
        return jsonify({'summary': "<p>El historial está vacío. ¡Escriban algo primero! ✍️</p>"})
    
    messages.reverse() # Ordenar cronológicamente
    
    # Formatear transcripción
    transcript_lines = []
    participants = set()
    for m in messages:
        # Ignorar mensajes multimedia largos en el prompt
        body = "Adjunto multimedia" if "http" in m.body else m.body
        transcript_lines.append(f"{m.user.name}: {body}")
        participants.add(m.user.name)
        
    transcript = "\n".join(transcript_lines)
    
    # --- INTEGRACIÓN IA (Mock/Placeholder) ---
    # Aquí puedes descomentar e integrar OpenAI:
    # try:
    #     import openai
    #     openai.api_key = "TU_API_KEY"
    #     resp = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": "Resume esta conversación de chat en puntos clave, con tono casual."},
    #             {"role": "user", "content": transcript}
    #         ]
    #     )
    #     ai_summary = resp.choices[0].message.content
    # except: ai_summary = "Error conectando con IA."
    
    # Generamos un resumen estadístico simulado por ahora
    import random
    top_emojis = random.choice(['🔥', '💡', '🤔', '🚀', '❤️'])
    
    simulated_summary = f"""
    <div style="background: linear-gradient(135deg, rgba(139, 93, 255, 0.1), rgba(0,0,0,0)); padding:20px; border-radius:12px; border:1px solid rgba(139, 93, 255, 0.2);">
        <h4 style="margin-top:0; color: #b197fc;">📝 Resumen de la Sesión</h4>
        <p>Se han analizado los últimos <strong>{len(messages)} mensajes</strong>.</p>
        
        <p><strong>👥 Participantes:</strong> {', '.join(participants)}</p>
        
        <p><strong>🔍 Puntos destacados (Simulados):</strong></p>
        <ul>
            <li>La conversación ha sido muy activa. {top_emojis}</li>
            <li>Se han intercambiado aproximadamente <strong>{len(transcript.split())} palabras</strong>.</li>
            <li>{random.choice(['Parece que están planeando algo interesante.', 'Hubo mucho debate sobre el diseño.', 'El ambiente general es positivo.'])}</li>
        </ul>
        
        <hr style="border-color:rgba(255,255,255,0.1);">
        <small style="color:#aaa;">*Nota: Para activar resúmenes semánticos reales, añade tu API Key en la ruta <code>/summarize</code> en el backend.*</small>
    </div>
    """
    
    return jsonify({'summary': simulated_summary})

@main_bp.route('/rename_whiteboard', methods=['POST'])
@login_required
def rename_whiteboard():
    from app.models import Whiteboard
    wb_id = request.form.get('wb_id')
    new_name = request.form.get('new_name')
    
    wb = Whiteboard.query.get(wb_id)
    if wb:
        # Opcional: Verificar permisos de sala (wb.room_id in current_user.rooms...)
        wb.name = new_name
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Pizarra no encontrada'}), 404

@main_bp.route('/delete_whiteboard', methods=['POST'])
@login_required
def delete_whiteboard():
    from app.models import Whiteboard
    wb_id = request.form.get('wb_id')
    
    wb = Whiteboard.query.get(wb_id)
    if wb:
        db.session.delete(wb)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Pizarra no encontrada'}), 404

@main_bp.route('/update_room', methods=['POST'])
@login_required
def update_room():
    from app.models import Room
    
    room_id = request.form.get('room_id')
    name = request.form.get('name')
    avatar_url = request.form.get('avatar_url')
    
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Grupo no encontrado'}), 404
        
    # Seguridad básica
    if room.is_private:
        # Por ahora evitamos editar privados para no confundir usuarios
        pass
    else:
        if name:
            room.name = name
        if avatar_url:
            room.avatar_url = avatar_url
            
    db.session.commit()
    return redirect(url_for('main.chat', room_id=room.id))