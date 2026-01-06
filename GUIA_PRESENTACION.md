# 🎓 Guía para Presentar tu Proyecto Chat

¡Felicidades por terminar tu proyecto! Aquí tienes los pasos para presentarlo en clase y que todos puedan unirse.

## ⚡ Opción A: Ngrok (Recomendada)
*Ideal para evitar problemas con el WiFi de la escuela.*

1.  **Descargar**: Baja [ngrok](https://download.ngrok.com/windows) y descomprímelo.
2.  **Iniciar Servidor**: 
    - En tu carpeta del proyecto, ejecuta: `python app.py`
    - Asegúrate de que no haya errores.
3.  **Iniciar Túnel**:
    - Abre `ngrok.exe`.
    - Escribe: `ngrok http 5000`
    - Presiona Enter.
4.  **Compartir**:
    - Copia la dirección que aparece en `Forwarding` (ej: `https://a1b2-c3d4.ngrok-free.app`).
    - **¡OJO!**: Pásales la dirección `https`, no la http.
    - Escribe esa dirección en la pizarra o envíala al grupo de clase.

---

## 🏠 Opción B: WiFi Local
*Solo funciona si todos están en la MISMA red WiFi y la escuela no bloquea conexiones.*

1.  Abre una terminal (PowerShell o CMD).
2.  Escribe `ipconfig` y busca **Dirección IPv4** (suele empezar por 192.168.x.x o 10.x.x.x).
3.  Tu enlace es: `http://TU_IP:5000` (ej: `http://192.168.1.85:5000`).

---

## 🎨 Tips para la Demo
*   **Modo Incógnito**: Abre una ventana de incógnito para simular ser un segundo usuario y mostrar el chat en tiempo real tú solo si nadie se conecta rápido.
*   **Pizarra**: Dibuja algo colaborativo. ¡Pide a un voluntario que dibuje contigo!
*   **Resumen IA**: Haz que la gente escriba mucho y luego pulsa el botón 🤖 para que vean la magia.
