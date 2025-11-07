document.addEventListener('DOMContentLoaded', () => {
  const boot = document.getElementById('boot');
  if (!boot) return; // no estamos en chat

  const CURRENT_USER_ID = parseInt(boot.dataset.uid, 10);
  const ROOM_ID = parseInt(boot.dataset.room, 10);

  const socket = io();

  const messageForm = document.getElementById('message-form');
  const messageInput = document.getElementById('message-input');
  const messagesDiv = document.getElementById('messages');

  socket.on('connect', () => {
    socket.emit('join', { room_id: ROOM_ID });
  });

  if (messageForm) {
    messageForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const body = (messageInput.value || '').trim();
      if (!body) return;
      socket.emit('message', { room_id: ROOM_ID, body });
      messageInput.value = '';
    });
  }

  socket.on('message', (data) => {
    const isMine = data.user_id === CURRENT_USER_ID;
    const el = document.createElement('div');
    el.className = 'message ' + (isMine ? 'sent' : 'received') + ' appear';
    const time = new Date(data.ts || Date.now()).toLocaleTimeString();
    el.innerHTML = `
      <strong>${data.user || 'Usuario'}</strong>
      <span class="timestamp">[${time}]</span>
      <div>${data.body}</div>
    `;
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    setTimeout(() => el.classList.remove('appear'), 400);
  });

  socket.on('system', (data) => {
    const el = document.createElement('div');
    el.className = 'message received appear';
    el.innerHTML = `<em>${data.msg}</em>`;
    messagesDiv.appendChild(el);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    setTimeout(() => el.classList.remove('appear'), 400);
  });
});
