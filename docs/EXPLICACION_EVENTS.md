# Explicación Técnica: `app/main/events.py`

Este módulo implementa la capa de **controladores de eventos** para la comunicación WebSocket utilizando `flask-socketio`.

## Estructura y Flujo de Datos

### 1. Registro de Handlers
La función `register_socketio_handlers(socketio)` encapsula la lógica para evitar importaciones circulares con la instancia principal de la aplicación.

### 2. Evento `join`
**Trigger**: Cliente se conecta a una sala.
**Lógica**:
- Recibe `room_id`.
- `join_room(room_id)`: Suscribe el socket del cliente al canal de broadcast de esa sala.
- `emit("system")`: Notifica a los demás suscriptores del canal que un usuario ha entrado.

### 3. Evento `message`
**Trigger**: Cliente envía un mensaje.
**Lógica**:
1.  **Validación**: Asegura que el cuerpo del mensaje no esté vacío.
2.  **Persistencia (ORM)**:
    -   Crea instancia de `Message` (Modelo definido en `models.py`).
    -   `db.session.add()`: Añade a la transacción.
    -   `db.session.commit()`: Persiste en SQLite.
3.  **Broadcast**:
    -   `emit("message")`: Envía el payload JSON (incluyendo timestamp generado por DB) a todos los clientes en el `room_id`.

## Dependencias Clave
-   **`flask_socketio`**: Manejo de protocolo WebSocket/polling.
-   **`flask_login`**: Acceso a `current_user` para autenticación y atribución de mensajes.
-   **`app.models`**: Acceso a la capa de datos (`db`, `Message`).
