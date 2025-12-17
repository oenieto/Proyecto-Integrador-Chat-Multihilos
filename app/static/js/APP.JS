document.addEventListener('DOMContentLoaded', () => {

    // --- Global Theme Logic ---
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }

    const boot = document.getElementById('boot');

    if (boot) {

        const CURRENT_USER_ID = parseInt(boot.dataset.uid, 10);
        const ROOM_ID = parseInt(boot.dataset.room, 10);

        const socket = io();

        const messageForm = document.getElementById('message-form');
        const messageInput = document.getElementById('message-input');
        const messagesDiv = document.getElementById('messages');

        if (!messagesDiv) {
            console.error("¡ERROR CRÍTICO! No se encontró el div #messages");
        } else {
            console.log("¡Éxito! Div #messages encontrado.");
        }

        socket.on('connect', () => {
            console.log('Socket conectado. Uniéndose a la sala:', ROOM_ID);
            socket.emit('join', { room_id: ROOM_ID });
        });

        if (messageForm) {
            console.log("¡Éxito! Formulario de mensaje encontrado.");

            messageForm.addEventListener('submit', (e) => {
                console.log("Submit detectado, previniendo recarga...");
                e.preventDefault(); // ¡Esta es la línea clave!

                const body = messageInput.value.trim();
                if (!body) return;

                console.log('Enviando mensaje:', body);
                socket.emit('message', { room_id: ROOM_ID, body });
                messageInput.value = '';
            });
        } else {
            console.error("¡ERROR CRÍTICO! No se encontró el formulario #message-form");
        }

        socket.on('message', (data) => {
            console.log('¡MENSAJE RECIBIDO!', data);

            const isMine = data.user_id === CURRENT_USER_ID;
            const el = document.createElement('div');
            el.className = 'message ' + (isMine ? 'sent' : 'received') + ' appear';
            const time = new Date(data.ts).toLocaleTimeString();
            let content = data.body;
            // Check if it's an image URL
            if (data.body.startsWith('http') && (data.body.includes('.gif') || data.body.includes('.jpg') || data.body.includes('.png') || data.body.includes('.webp'))) {
                content = `<img src="${data.body}" style="max-width: 200px; border-radius: 8px; display: block; margin-top: 5px;">`;
            }

            el.innerHTML = `
                <strong>${data.user}</strong>
                <span class="timestamp">[${time}]</span>
                <div>${content}</div>
            `;

            if (messagesDiv) {
                messagesDiv.appendChild(el);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        });

        socket.on('system', (data) => {
            console.log('¡MENSAJE DE SISTEMA RECIBIDO!', data);

            const el = document.createElement('div');
            el.className = 'message received appear';
            el.innerHTML = `<em>${data.msg}</em>`;

            if (messagesDiv) {
                messagesDiv.appendChild(el);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        });

    } // --- Fin del 'if (boot)' ---

}); // --- Fin del 'DOMContentLoaded' ---