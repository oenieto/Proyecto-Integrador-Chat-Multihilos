// Variables globales para lógica de UI
let replyingToId = null;
let CURRENT_USER_ID = null;
let socket = null;

document.addEventListener('DOMContentLoaded', () => {

    // --- Global Theme Logic ---
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }

    const boot = document.getElementById('boot');

    if (boot) {
        CURRENT_USER_ID = parseInt(boot.dataset.uid, 10);
        const ROOM_ID = parseInt(boot.dataset.room, 10);

        // Iniciar Socket
        socket = io();

        const messageForm = document.getElementById('message-form');
        const messageInput = document.getElementById('message-input');
        const messagesDiv = document.getElementById('messages');
        const replyPreviewBar = document.getElementById('reply-preview-bar');

        socket.on('connect', () => {
            console.log('Socket conectado. Uniéndose a la sala:', ROOM_ID);
            socket.emit('join', { room_id: ROOM_ID });
        });

        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const body = messageInput.value.trim();
                if (!body) return;

                const payload = { room_id: ROOM_ID, body };
                if (replyingToId) {
                    payload.parent_id = replyingToId;
                    cancelReply(); // Limpiar estado UI
                }

                socket.emit('message', payload);
                messageInput.value = '';
            });
        }

        socket.on('message', (data) => {
            const el = document.createElement('div');
            el.id = `msg-${data.id}`;
            el.dataset.id = data.id;
            el.className = 'message ' + (data.user_id === CURRENT_USER_ID ? 'sent' : 'received') + ' appear';
            el.ondblclick = () => toggleActions(data.id);

            el.innerHTML = renderMessageContent(data);

            if (messagesDiv) {
                messagesDiv.appendChild(el);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        });

        socket.on('message_updated', (data) => {
            const el = document.getElementById(`msg-${data.id}`);
            if (el) {
                // Actualizar contenido manteniendo las clases base pero actualizando estado
                el.innerHTML = renderMessageContent(data);

                // Actualizar clase si cambió algo relevante (raro en update, pero posible)
            }
        });

        socket.on('system', (data) => {
            const el = document.createElement('div');
            el.className = 'message received appear';
            el.innerHTML = `<em>${data.msg}</em>`;
            if (messagesDiv) {
                messagesDiv.appendChild(el);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        });
    }
});

// --- Helper Functions (Global Scope) ---

// --- Helper Functions (Global Scope) ---

function renderMessageContent(m) {
    const isMine = m.user_id === CURRENT_USER_ID;

    // 1. Reply Context
    let replyHTML = '';
    if (m.parent_id) {
        replyHTML = `
        <div class="reply-context" onclick="scrollToMessage('${m.parent_id}')">
            <span class="reply-bar"></span>
            <small>Replying to <strong>${m.parent_user || 'Usuario'}</strong></small>
            <div class="reply-excerpt">${m.parent_body || '...'}</div>
        </div>`;
    }

    // 2. Body Content
    let bodyHTML = '';
    if (m.is_deleted) {
        bodyHTML = `<div class="msg-content"><em style="color:var(--muted); font-style: italic;">🚫 Este mensaje fue eliminado</em></div>`;
    } else {
        let content = m.body || '';
        // Normalizar extracción de extensión
        const cleanContent = content.split('?')[0];
        const ext = cleanContent.includes('.') ? cleanContent.split('.').pop().toLowerCase() : '';

        // Detectar si es ruta de archivo (absoluta o relativa)
        const isFile = content.startsWith('http') || content.startsWith('/static/');

        if (isFile && ['gif', 'jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
            content = `<img src="${content}" style="max-width: 200px; border-radius: 8px; display: block; margin-top: 5px;" loading="lazy">`;
        } else if (isFile && ['webm', 'mp3', 'wav', 'ogg'].includes(ext)) {
            content = `<audio controls src="${content}" style="max-width: 250px; margin-top:5px;"></audio>`;
        } else if (isFile && content.includes('/static/uploads/')) {
            content = `<div class="file-attachment"><a href="${content}" target="_blank" style="color:var(--purple);">📄 Ver archivo adjunto (${ext})</a></div>`;
        }

        bodyHTML = `<div class="msg-content">${content}</div>`;
    }

    // 3. Reactions
    let reactionsHTML = '';
    if (m.reactions && Object.keys(m.reactions).length > 0) {
        let pills = '';
        for (const [emoji, users] of Object.entries(m.reactions)) {
            pills += `<span class="reaction-pill" title="${users.join(', ')}">${emoji} ${users.length > 1 ? users.length : ''}</span>`;
        }
        reactionsHTML = `<div class="reactions-display">${pills}</div>`;
    }

    // 4. Actions Menu (Hover Style)
    let actionsHTML = '';
    if (!m.is_deleted) {
        // Escapeo básico
        const safeBody = (m.body || '').replace(/'/g, "\\'");

        // Botón Eliminar solo si es mío
        let deleteBtn = '';
        if (isMine) {
            deleteBtn = `<button onclick="event.stopPropagation(); deleteMessage('${m.id}')" style="color:#ff6b6b" title="Eliminar">🗑️</button>`;
        }

        actionsHTML = `
        <div class="msg-actions" id="actions-${m.id}">
            <button onclick="startReply('${m.id}', '${m.user}', '${safeBody}')" title="Responder">↩️</button>
            <button onclick="react('${m.id}', '❤️')" title="Me encanta">❤️</button>
            <button onclick="react('${m.id}', '😂')" title="Me divierte">😂</button>
            <button onclick="react('${m.id}', '👍')" title="Me gusta">👍</button>
            ${deleteBtn}
        </div>`;
    }

    // Timestamp & Deleted Tag
    const time = m.created_at || m.timestamp;
    const deletedTag = m.is_deleted ? '<span class="deleted-tag">ELIMINADO</span>' : '';

    return `
        ${replyHTML}
        <strong>${m.user}</strong>
        <span class="timestamp">[${time}] ${deletedTag}</span>
        ${bodyHTML}
        ${reactionsHTML}
        ${actionsHTML}
    `;
}

window.startReply = function (id, user, body) {
    replyingToId = id;
    const bar = document.getElementById('reply-preview-bar');
    document.getElementById('reply-to-user').innerText = user;
    document.getElementById('reply-to-text').innerText = body.substring(0, 50) + (body.length > 50 ? '...' : '');
    bar.style.display = 'flex';
    document.getElementById('message-input').focus();
}

window.cancelReply = function () {
    replyingToId = null;
    document.getElementById('reply-preview-bar').style.display = 'none';
}

window.deleteMessage = function (id) {
    // Eliminamos confirmación nativa para mayor fluidez.
    // Si quisieramos seguridad, podríamos implementar un toast/undo, pero esto responde a la petición de rapidez.
    socket.emit('delete_message', { message_id: id });
}

window.react = function (id, emoji) {
    socket.emit('react_message', { message_id: id, emoji: emoji });
}

window.scrollToMessage = function (id) {
    const el = document.getElementById(`msg-${id}`);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.background = 'rgba(255,255,255,0.1)';
        setTimeout(() => el.style.background = '', 1000);
    } else {
        alert("Mensaje original no encontrado (quizás es muy antiguo)");
    }
}

// --- Upload & Recording Logic ---

window.uploadFile = function (file) {
    if (!file) return;

    // Feedback visual simple
    const btn = document.querySelector('button[onclick*="file-upload-input"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                // Enviar como mensaje normal
                document.getElementById('message-input').value = data.url;
                // Disparar envío
                const form = document.getElementById('message-form');
                form.dispatchEvent(new Event('submit'));
            } else {
                alert('Error subiendo archivo: ' + (data.error || 'Desconocido'));
            }
        })
        .catch(err => {
            console.error(err);
            alert('Error de conexión al subir archivo');
        })
        .finally(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            // Limpiar input file para permitir subir el mismo archivo consecutivamente si se desea
            document.getElementById('file-upload-input').value = '';
        });
}

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

window.toggleRecording = async function () {
    const btn = document.getElementById('mic-btn');

    if (!isRecording) {
        // Iniciar grabación
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                // Convertir Blob a File para subirlo. Nombre único temporal.
                const file = new File([audioBlob], "voice_note.webm", { type: 'audio/webm' });
                uploadFile(file);

                // Detener tracks para liberar microfono
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            isRecording = true;
            btn.innerHTML = '🟥'; // Stop icon
            btn.style.color = '#ff4d4d';
            btn.classList.add('pulse'); // Asumimos que podemos añadir una clase CSS para animación
        } catch (err) {
            console.error(err);
            alert("No se pudo acceder al micrófono. Asegúrate de dar permisos.");
        }
    } else {
        // Parar grabación
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        isRecording = false;
        btn.innerHTML = '🎤';
        btn.style.color = '';
        btn.classList.remove('pulse');
    }
}

// --- Whiteboard Logic ---
let canvas, ctx;
let drawing = false;
let currentX = 0; let currentY = 0;
let wbColorVal = '#ffffff';
let wbWidthVal = 2;
let wbTool = 'pencil'; // pencil, rect, circle, triangle, line
let wbToolType = 'normal'; // normal, marker, pen
let snapshot;

// --- Whiteboard Selection & Logic ---

window.openWbSelection = function () {
    // Si la pizarra ya está abierta, la cerramos
    const wbModal = document.getElementById('whiteboard-modal');
    if (wbModal.style.display === 'flex') {
        wbModal.style.display = 'none';
        return;
    }
    // Si no, abrimos el menú de selección
    const selModal = document.getElementById('wb-selection-modal');
    selModal.style.display = 'flex';
    resetWbSelection();
}

// Mantenemos esta función para el botón 'X' dentro de la pizarra
window.toggleWhiteboard = function () {
    const modal = document.getElementById('whiteboard-modal');
    modal.style.display = 'none';
}

window.closeWbSelection = function () {
    document.getElementById('wb-selection-modal').style.display = 'none';
}

window.resetWbSelection = function () {
    document.getElementById('wb-options-main').style.display = 'flex';
    document.getElementById('wb-selection-list-container').style.display = 'none';
}

window.startNewWhiteboard = function () {
    closeWbSelection();
    const wbModal = document.getElementById('whiteboard-modal');
    wbModal.style.display = 'flex';
    initCanvas();
    // Opcional: limpiar si se quisiera empezar fresco, pero respetamos colaboración
}

window.showSavedWbList = function () {
    document.getElementById('wb-options-main').style.display = 'none';
    const listContainer = document.getElementById('wb-selection-list-container');
    listContainer.style.display = 'flex';

    const list = document.getElementById('wb-selection-items');
    list.innerHTML = '<div style="text-align:center; color:#ccc; padding:20px;">Cargando...</div>';

    const boot = document.getElementById('boot');
    const room_id = boot ? parseInt(boot.dataset.room) : 1;

    fetch(`/whiteboards/${room_id}`)
        .then(r => r.json())
        .then(data => {
            list.innerHTML = '';
            if (!data || data.length === 0) {
                list.innerHTML = '<div style="text-align:center; opacity:0.6; padding:10px;">No hay pizarras guardadas</div>';
                return;
            }

            data.forEach(wb => {
                const div = document.createElement('div');
                div.className = 'wb-list-item-row';
                div.innerHTML = `
                    <div class="wb-list-item-name">📄 ${wb.name} <small style="opacity:0.5; font-size:0.7em;">(${wb.created_at})</small></div>
                    <div class="wb-list-item-actions">
                        <button class="wb-action-btn-mini edit" onclick="renameWb(event, ${wb.id}, '${wb.name}')" title="Renombrar">✏️</button>
                        <button class="wb-action-btn-mini del" onclick="deleteWb(event, ${wb.id})" title="Borrar">🗑️</button>
                    </div>
                `;
                // Cargar en canvas al hacer click
                div.onclick = () => loadWbToCanvas(wb.url);
                list.appendChild(div);
            });
        });
}

window.renameWb = function (e, id, oldName) {
    e.stopPropagation();
    let newName = prompt("Nuevo nombre:", oldName);
    if (!newName || newName === oldName) return;

    const fd = new FormData();
    fd.append('wb_id', id);
    fd.append('new_name', newName);

    fetch('/rename_whiteboard', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            if (d.success) showSavedWbList(); // Recargar lista
            else alert(d.error);
        });
}

window.deleteWb = function (e, id) {
    e.stopPropagation();
    // Confimación 1
    if (!confirm("⚠️ ¿Estás seguro de que quieres ELIMINAR esta pizarra?")) return;

    // Confirmación 2
    if (!confirm("⛔ ¡Esta acción es irreversible! ¿Confirmas el borrado definitivo?")) return;

    const fd = new FormData();
    fd.append('wb_id', id);

    fetch('/delete_whiteboard', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            if (d.success) showSavedWbList(); // Recargar lista
            else alert(d.error);
        });
}

window.loadWbToCanvas = function (imageUrl) {
    closeWbSelection();
    const wbModal = document.getElementById('whiteboard-modal');
    wbModal.style.display = 'flex';
    initCanvas();

    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.src = imageUrl;
    img.onload = function () {
        if (ctx) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }
    }
}

window.wbSetTool = function (tool) {
    if (['pencil', 'marker', 'pen'].includes(tool)) {
        wbTool = 'pencil';
        wbToolType = tool;
        const icon = tool === 'marker' ? '🖍️' : (tool === 'pen' ? '✒️' : '✏️');
        document.getElementById('tool-pencil').innerHTML = icon;
        setActiveBtn('tool-pencil');
    } else if (tool === 'text') {
        wbTool = 'text';
        setActiveBtn('tool-text');
    } else {
        wbTool = tool;
        setActiveBtn('tool-shapes');
    }
}

function setActiveBtn(id) {
    document.querySelectorAll('.wb-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(id);
    if (btn) btn.classList.add('active');
}

function initCanvas() {
    canvas = document.getElementById('wb-canvas');
    ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth * 0.8;
    canvas.height = window.innerHeight * 0.8;

    canvas.addEventListener('mousedown', onMouseDown, false);
    canvas.addEventListener('mouseup', onMouseUp, false);
    canvas.addEventListener('mousemove', onMouseMove, false);

    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchend', onMouseUp, false);
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });

    if (!socket.hasListeners('draw')) {
        socket.on('draw', onDrawingEvent);
        socket.on('clear_board', clearCanvas);
    }
}

function getToolStyle() {
    let width = wbWidthVal;
    let alpha = 1;
    let cap = 'round';

    if (wbTool === 'pencil') {
        if (wbToolType === 'marker') {
            width = wbWidthVal * 4;
            alpha = 0.4;
            cap = 'square';
        } else if (wbToolType === 'pen') {
            width = 1;
        }
    }
    return { width, alpha, cap };
}

function onMouseDown(e) {
    drawing = true;
    const rect = canvas.getBoundingClientRect();
    currentX = e.clientX - rect.left;
    currentY = e.clientY - rect.top;
    if (wbTool !== 'pencil' && wbTool !== 'text') snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
}
function onTouchStart(e) {
    if (e.target == canvas) e.preventDefault();
    drawing = true;
    const rect = canvas.getBoundingClientRect();
    currentX = e.touches[0].clientX - rect.left;
    currentY = e.touches[0].clientY - rect.top;
    if (wbTool !== 'pencil' && wbTool !== 'text') snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
}

function onMouseUp(e) {
    if (!drawing) return;
    drawing = false;
    const rect = canvas.getBoundingClientRect();
    let clientX = e.clientX || (e.changedTouches ? e.changedTouches[0].clientX : 0);
    let clientY = e.clientY || (e.changedTouches ? e.changedTouches[0].clientY : 0);
    let endX = clientX - rect.left;
    let endY = clientY - rect.top;

    const style = getToolStyle();

    if (wbTool === 'text') {
        let text = prompt("Escribe tu texto:", "");
        if (text) {
            drawText(endX, endY, text, wbColorVal, style.width * 8 + 10, true);
        }
    } else if (wbTool !== 'pencil') {
        drawShape(currentX, currentY, endX, endY, wbTool, wbColorVal, style.width, true);
    } else {
        emitDraw(currentX, currentY, currentX, currentY, wbColorVal, style.width, wbToolType);
    }
}

function onMouseMove(e) {
    if (!drawing) return;
    const rect = canvas.getBoundingClientRect();
    handleMove(e.clientX - rect.left, e.clientY - rect.top);
}
function onTouchMove(e) {
    if (!drawing) return;
    if (e.target == canvas) e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    handleMove(e.touches[0].clientX - rect.left, e.touches[0].clientY - rect.top);
}

function handleMove(nextX, nextY) {
    const style = getToolStyle();

    if (wbTool === 'pencil') {
        drawLine(currentX, currentY, nextX, nextY, wbColorVal, style.width, style.cap, style.alpha, true, wbToolType);
        currentX = nextX;
        currentY = nextY;
    } else if (wbTool !== 'text') {
        ctx.putImageData(snapshot, 0, 0);
        drawShape(currentX, currentY, nextX, nextY, wbTool, wbColorVal, style.width, false);
    }
}

function drawLine(x0, y0, x1, y1, color, width, cap, alpha, emit, toolType) {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = cap || 'round';
    ctx.globalAlpha = alpha || 1;
    ctx.stroke();
    ctx.globalAlpha = 1;

    if (emit) emitDraw(x0, y0, x1, y1, color, width, toolType);
}

function drawShape(x0, y0, x1, y1, tool, color, width, emit) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.globalAlpha = 1;

    if (tool === 'rect') {
        ctx.rect(x0, y0, x1 - x0, y1 - y0);
    } else if (tool === 'circle') {
        let r = Math.sqrt(Math.pow(x1 - x0, 2) + Math.pow(y1 - y0, 2));
        ctx.arc(x0, y0, r, 0, 2 * Math.PI);
    } else if (tool === 'triangle') {
        ctx.moveTo(x0 + (x1 - x0) / 2, y0);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x0, y1);
        ctx.closePath();
    } else if (tool === 'line') {
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
    }

    ctx.stroke();

    if (emit) {
        emitDrawShape(x0, y0, x1, y1, tool, color, width);
    }
}

function drawText(x, y, text, color, size, emit) {
    ctx.font = `${size}px sans-serif`;
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);

    if (emit) emitDrawText(x, y, text, color, size);
}

function emitDraw(x0, y0, x1, y1, color, width, toolType) {
    const boot = document.getElementById('boot');
    socket.emit('draw', {
        type: 'line',
        room_id: boot ? parseInt(boot.dataset.room) : 1,
        x0: x0 / canvas.width, y0: y0 / canvas.height,
        x1: x1 / canvas.width, y1: y1 / canvas.height,
        color, width, toolType
    });
}
function emitDrawShape(x0, y0, x1, y1, tool, color, width) {
    const boot = document.getElementById('boot');
    socket.emit('draw', {
        type: 'shape', tool,
        room_id: boot ? parseInt(boot.dataset.room) : 1,
        x0: x0 / canvas.width, y0: y0 / canvas.height,
        x1: x1 / canvas.width, y1: y1 / canvas.height,
        color, width
    });
}
function emitDrawText(x, y, text, color, size) {
    const boot = document.getElementById('boot');
    socket.emit('draw', {
        type: 'text',
        room_id: boot ? parseInt(boot.dataset.room) : 1,
        x0: x / canvas.width, y0: y / canvas.height,
        text, color, size
    });
}

function onDrawingEvent(data) {
    if (!canvas) return;
    const w = canvas.width;
    const h = canvas.height;

    if (data.type === 'shape') {
        drawShape(data.x0 * w, data.y0 * h, data.x1 * w, data.y1 * h, data.tool, data.color, data.width, false);
    } else if (data.type === 'text') {
        drawText(data.x0 * w, data.y0 * h, data.text, data.color, data.size, false);
    } else {
        let alpha = 1, cap = 'round';
        let width = data.width;
        if (data.toolType === 'marker') { alpha = 0.4; cap = 'square'; }

        drawLine(data.x0 * w, data.y0 * h, data.x1 * w, data.y1 * h, data.color, width, cap, alpha, false);
    }
}

// --- Historial ---
window.wbSave = function () {
    console.log("wbSave called");
    let name = prompt("Nombre para guardar esta pizarra:", "Diseño " + new Date().toLocaleTimeString());
    if (name === null) return;

    const canvas = document.getElementById('wb-canvas');
    const dataURL = canvas.toDataURL('image/png');
    const boot = document.getElementById('boot');
    const room_id = boot ? parseInt(boot.dataset.room) : 1;

    const fd = new FormData();
    fd.append('room_id', room_id);
    fd.append('image', dataURL);
    fd.append('name', name);

    // Feedback visual
    const btn = document.querySelector('button[title="Guardar"]'); // Selector más robusto
    if (btn) btn.innerHTML = '⏳';

    fetch('/save_whiteboard', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
            if (btn) btn.innerHTML = '💾';
            if (data.url) {
                alert('¡Guardado exitoso!');
                const sb = document.getElementById('wb-history-sidebar');
                if (sb && sb.classList.contains('open')) loadWbHistory();
            } else {
                alert('Error: ' + data.error);
            }
        }).catch(e => {
            console.error(e);
            if (btn) btn.innerHTML = '💾';
            alert('Error de red al guardar');
        });
}

window.toggleWbHistory = function () {
    console.log("toggleWbHistory called");
    const sb = document.getElementById('wb-history-sidebar');
    if (!sb) { alert("Error: Sidebar no encontrado"); return; }

    sb.classList.toggle('open');
    if (sb.classList.contains('open')) {
        loadWbHistory();
    }
}

function loadWbHistory() {
    const boot = document.getElementById('boot');
    const room_id = boot ? parseInt(boot.dataset.room) : 1;
    const list = document.getElementById('wb-history-list');
    if (!list) return;

    list.innerHTML = '<div style="color:white;text-align:center;padding:20px;">Cargando...</div>';

    fetch(`/whiteboards/${room_id}`)
        .then(r => r.json())
        .then(data => {
            list.innerHTML = '';
            if (!data || data.length === 0) {
                list.innerHTML = '<div style="text-align:center; opacity:0.6; padding:20px;">Sin historial</div>';
                return;
            }

            data.forEach(wb => {
                const div = document.createElement('div');
                div.className = 'wb-item';
                div.innerHTML = `
                <img src="${wb.url}" alt="${wb.name}">
                <small><strong>${wb.name}</strong><br>${wb.created_at}</small>
            `;
                div.onclick = () => window.open(wb.url, '_blank');
                list.appendChild(div);
            });
        }).catch(err => {
            list.innerHTML = '<div style="color:red;text-align:center;">Error al cargar</div>';
        });
}

window.wbSetColor = (c) => wbColorVal = c;
window.wbSetWidth = (w) => wbWidthVal = w;
window.wbClear = function () {
    const boot = document.getElementById('boot');
    if (boot) socket.emit('clear_board', { room_id: boot.dataset.room });
    clearCanvas();
}
function clearCanvas() {
    if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
}
function throttle(callback, delay) {
    let previousCall = new Date().getTime();
    return function () {
        const time = new Date().getTime();
        if ((time - previousCall) >= delay) {
            previousCall = time;
            callback.apply(null, arguments);
        }
    };
}

// --- AI Summary ---
window.requestSummary = function () {
    const modal = document.getElementById('summary-modal');
    const content = document.getElementById('summary-content');
    modal.style.display = 'flex';

    // Reset loading state
    content.innerHTML = `
        <div style="text-align:center; padding: 40px;">
            <div class="pulse" style="font-size: 3rem; margin-bottom:20px;">🤖</div>
            <p>Leyendo mensajes...</p>
        </div>
    `;

    const boot = document.getElementById('boot');
    const room_id = boot ? boot.dataset.room : 1;

    fetch(`/summarize/${room_id}`)
        .then(r => r.json())
        .then(data => {
            if (data.summary) {
                content.innerHTML = data.summary;
            } else {
                content.innerHTML = `<div style="color:#ff6b6b; text-align:center; padding:20px;">
                <strong>Error:</strong> ${data.error}
            </div>`;
            }
        })
        .catch(err => {
            console.error(err);
            content.innerHTML = '<div style="color:#ff6b6b; text-align:center; padding:20px;">Error de conexión con el servidor.</div>';
        });
}

window.closeSummaryModal = function () {
    document.getElementById('summary-modal').style.display = 'none';
}