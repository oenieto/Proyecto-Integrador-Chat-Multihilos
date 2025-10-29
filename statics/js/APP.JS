console.log("¡JavaScript del chat cargado!");

// Aquí puedes añadir lógica interactiva para el formulario de registro si es necesario.
// Por ejemplo, para manejar el envío del formulario.

document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.querySelector('.account-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Previene el envío tradicional del formulario
            console.log("Formulario de cuenta enviado (simulado).");
            // Aquí puedes añadir lógica para:
            // 1. Recopilar los datos del formulario.
            // 2. Enviar los datos a tu backend Flask usando fetch().
            // 3. Manejar la respuesta del backend (ej. redirigir o mostrar un mensaje).
            alert("Cuenta creada (funcionalidad no implementada aún, solo simulación).");
        });
    }
});