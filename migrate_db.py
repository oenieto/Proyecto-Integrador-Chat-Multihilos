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

# Verificar qué columnas existen en la tabla room
cursor.execute("PRAGMA table_info(room)")
room_columns = [column[1] for column in cursor.fetchall()]

print("Columnas actuales en 'room':", room_columns)

# Agregar columna faltante a la tabla room
if 'avatar_url' not in room_columns:
    print("Agregando columna 'avatar_url' a la tabla room...")
    cursor.execute("ALTER TABLE room ADD COLUMN avatar_url VARCHAR(255)")

conn.commit()
conn.close()

print("✅ Migración completada exitosamente!")
