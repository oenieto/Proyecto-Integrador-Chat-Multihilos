# Proyecto Integrador: Servidor de Chat Multihilo (Web)

Este proyecto desarrolla un servidor de chat concurrente como aplicación web utilizando Python con Flask para el backend y HTML, CSS, JavaScript para el frontend.

## Requisitos previos

- Python 3.8 o superior
- Un navegador web moderno (Edge, Chrome, Firefox)

## Configuración e Instalación

1.  **Crear y activar un entorno virtual (recomendado):**

    ```bash
    # En Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

2.  **Instalar dependencias:**

    ```bash
    pip install -r requerimientos.txt
    ```

## Cómo ejecutar la aplicación

Tienes dos formas de ejecutar el proyecto:

### 1. Modo Servidor Web (Navegador)

Para abrir la aplicación en tu navegador predeterminado:

```bash
python app.py
```

Luego ve a `http://127.0.0.1:5000` si no se abre automáticamente.

### 2. Modo Aplicación de Escritorio

Para ejecutarlo como una ventana nativa de escritorio:

```bash
python run_desktop.py
```

## Solución de problemas comunes

- **Error "No module named..."**: Asegúrate de haber activado el entorno virtual (`.venv\Scripts\activate`) antes de ejecutar los comandos python.