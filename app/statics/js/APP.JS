// Cliente Socket.IO para la vista de chat
document.addEventListener('DOMContentLoaded', () => {
  // Solo corre en la página de chat (donde definimos ROOM_ID)
  if (typeof ROOM_ID === 'undefined') return;

  // Conexión
  const socket = io(); // mismo host/puerto

  // Elementos del DOM (IDs que acordamos)
  const messageForm = document.getElementById('message-form');
  const messageInput = document.getElementById('message-input');
  const messagesDiv = document.getElementById('messages');

  // Al conectar, únete a la sala actual
  socket.on('connect', () => {
    socket.emit('join', { room_id: ROOM_ID });
  });

  // Enviar mensaje (evento 'message' que maneja el server)
  if (messageForm) {
    messageForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const body = (messageInput.value || '').trim();
      if (!body) return;
      socket.emit('message', { room_id: ROOM_ID, body });
      messageInput.value = '';
    });
  }

  // Recibir mensajes del servidor
  socket.on('message', (data) => {
    const time = new Date(data.ts || Date.now()).toLocaleTimeString();
    const el = document.createElement('div');
    el.className = 'msg';
    el.innerHTML = `<b>${data.user || 'Usuario'}</b> <span class="time">${time}</span><p>${data.body}</p>`;
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  });

  // Mensajes de sistema (opcional)
  socket.on('system', (data) => {
    const el = document.createElement('div');
    el.className = 'msg';
    el.innerHTML = `<i>${data.msg}</i>`;
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  });

  // Scroll al final al cargar
  if (messagesDiv) messagesDiv.scrollTop = messagesDiv.scrollHeight;
});
