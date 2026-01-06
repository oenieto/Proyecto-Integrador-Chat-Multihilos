"""
Script de migración para agregar las nuevas columnas a la base de datos existente.
"""
import sqlite3
import os

# Ruta a la base de datos
DB_PATH = os.path.join('instance', 'chat.db')

if not os.path.exists(DB_PATH):
    print(f"Base de datos no encontrada en {DB_PATH}")
    print("Se creará automáticamente al iniciar la aplicación.")
    exit(0)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar qué columnas existen en la tabla user
cursor.execute("PRAGMA table_info(user)")
user_columns = [column[1] for column in cursor.fetchall()]

print("Columnas actuales en 'user':", user_columns)

# Agregar columnas faltantes a la tabla user
if 'phone_number' not in user_columns:
    print("Agregando columna 'phone_number' a la tabla user...")
    cursor.execute("ALTER TABLE user ADD COLUMN phone_number VARCHAR(20)")
    
if 'country_code' not in user_columns:
    print("Agregando columna 'country_code' a la tabla user...")
    cursor.execute("ALTER TABLE user ADD COLUMN country_code VARCHAR(5)")

# ... (código existente)

# Verificar qué columnas existen en la tabla message
cursor.execute("PRAGMA table_info(message)")
message_columns = [column[1] for column in cursor.fetchall()]
print("Columnas actuales en 'message':", message_columns)

if 'parent_id' not in message_columns:
    print("Agregando columna 'parent_id' a la tabla message...")
    cursor.execute("ALTER TABLE message ADD COLUMN parent_id INTEGER REFERENCES message(id)")

if 'is_deleted' not in message_columns:
    print("Agregando columna 'is_deleted' a la tabla message...")
    # SQLite no tiene un tipo BOOLEAN nativo estricto, usamos INTEGER 0/1, pero declaramos BOOLEAN para compatibilidad lógica
    cursor.execute("ALTER TABLE message ADD COLUMN is_deleted BOOLEAN DEFAULT 0")

if 'deleted_at' not in message_columns:
    print("Agregando columna 'deleted_at' a la tabla message...")
    cursor.execute("ALTER TABLE message ADD COLUMN deleted_at DATETIME")

# Crear tabla de reacciones si no existe
print("Verificando tabla 'message_reaction'...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS message_reaction (
    id INTEGER PRIMARY KEY,
    message_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(message_id) REFERENCES message(id),
    FOREIGN KEY(user_id) REFERENCES user(id)
)
""")

# Crear tabla de whiteboards si no existe
print("Verificando tabla 'whiteboard'...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS whiteboard (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(room_id) REFERENCES room(id)
)
""")

conn.commit()
conn.close()

print("✅ Migración Fase 1 (Social) completada exitosamente!")
