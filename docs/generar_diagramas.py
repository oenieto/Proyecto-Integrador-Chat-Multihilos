import os

def generar_diagrama_clases_web():
    """
    Genera el archivo .puml para el diagrama de clases de la arquitectura web.
    """
    # Contenido del diagrama que describe tu app Flask
    contenido_puml = """
@startuml
!theme spacelab

skinparam classAttributeIconSize 0
skinparam classBackgroundColor #2C2C2C
skinparam classBorderColor #4A90E2
skinparam classArrowColor #E0E0E0
skinparam classFontColor #E0E0E0

class FlaskApp <<(F,lightblue)>> {
  + app
  + run()
  + index()
}

class MessageAPI <<Resource>> {
  + get(session_id)
  + post(session_id)
}

class ChatService <<Singleton>> {
  - messages: list<Message>
  - users: dict<user_id, User>
  + get_messages_since(timestamp)
  + add_message(user, content)
  + get_active_users()
}

class User {
  - user_id: string
  - nick: string
}

class Message {
  - message_id: int
  - user: User
  - content: string
  - timestamp: datetime
}

FlaskApp -- MessageAPI : registers
MessageAPI -- ChatService : uses
ChatService o-- "*" Message : contains
ChatService o-- "*" User : contains
@enduml
"""
    # Guardar el archivo en la carpeta 'diagramas'
    diagram_path = os.path.join('diagramas', 'diagrama_clases_web.puml')
    
    # Asegurarse de que la carpeta 'diagramas' exista
    os.makedirs(os.path.dirname(diagram_path), exist_ok=True)
    
    with open(diagram_path, "w") as f:
        f.write(contenido_puml)
    print(f"✅ Archivo '{diagram_path}' generado.")


if __name__ == "__main__":
    generar_diagrama_clases_web()
    print("\n🚀 Diagrama para arquitectura web generado en la carpeta 'diagramas/'.")