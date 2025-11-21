# Arquitectura de Aplicación Web: Chat con Flask

El proyecto seguirá una arquitectura de 3 componentes principales:

1.  **Frontend (Cliente Web):** Una aplicación de una sola página (SPA) construida con **HTML, CSS y JavaScript**. Se ejecuta completamente en el navegador del usuario y es responsable de renderizar la interfaz (desde la carpeta `templates`) y manejar las interacciones del usuario (con archivos de `statics`).

2.  **Backend (Servidor API):** Un servidor web desarrollado en **Python con el framework Flask** (archivo `app.py`). Su responsabilidad es:
    * Servir la página HTML inicial.
    * Manejar la lógica del chat (registro de usuarios, recepción y envío de mensajes).
    * Exponer una **API REST** para que el frontend pueda comunicarse.

3.  **Comunicación (API REST con JSON):** El Frontend (JavaScript) se comunicará con el Backend (Flask) a través de peticiones HTTP. Los datos (mensajes nuevos, listas de usuarios, etc.) se intercambiarán en formato **JSON**.