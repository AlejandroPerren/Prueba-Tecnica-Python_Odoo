# `Prueba-Tecnica-Python_Odoo`: Microservicio de Sincronización de Pagos con Odoo

Este proyecto es un microservicio desarrollado con **FastAPI** que actúa como puente entre un sistema de procesamiento de pagos y **Odoo**, utilizando **MySQL** como base de datos local para registrar eventos.

## 🎯 Objetivo Principal

El objetivo del servicio es procesar eventos de "Pago Recibido" y realizar las siguientes acciones de forma coordinada:

1.  **Registrar un Asiento Contable en Odoo:** Crea un `account.move` (asiento contable) con líneas de débito y crédito predefinidas en la instancia de Odoo configurada.
2.  **Guardar Evento de Pago en MySQL:** Registra los detalles del pago en una tabla local `payment_events` en MySQL, incluyendo el monto, la fecha y el estado de sincronización.
3.  **Actualizar el Estado de Sincronización:** El evento en MySQL se actualiza a `COMPLETED` si la operación en Odoo es exitosa, o a `FAILED` si ocurre algún error durante la comunicación con la API de Odoo.

## 🏛 Arquitectura General

La aplicación sigue una arquitectura limpia y modular:

*   **FastAPI:** Proporciona la interfaz RESTful para recibir los eventos de pago.
*   **Servicios (Services):** Contienen la lógica de negocio y encapsulan las interacciones con sistemas externos (Odoo) y la base de datos local (MySQL).
*   **Modelos (Models):** Definen la estructura de datos para la base de datos MySQL (SQLAlchemy ORM).
*   **Esquemas (Schemas):** Definen la estructura de los datos de entrada y salida de la API (Pydantic).
*   **Configuración (Config):** Centraliza la gestión de las variables de entorno.

## 🚀 Cómo Empezar

Para poner en marcha este proyecto, elige la opción que mejor se adapte a tu entorno:

*   **Configuración Específica de Odoo:** Si necesitas saber qué configurar en tu instancia de Odoo para que la aplicación funcione, consulta [README_ODOO.md](./README_ODOO.md).
*   **Ejecución Local (sin Docker):** Si prefieres configurar y ejecutar la aplicación directamente en tu máquina local, consulta [README_LOCAL.md](./README_LOCAL.md).
*   **Despliegue con Docker Compose:** Para una configuración más sencilla y portable utilizando contenedores Docker, consulta [README_DOCKER.md](./README_DOCKER.md).