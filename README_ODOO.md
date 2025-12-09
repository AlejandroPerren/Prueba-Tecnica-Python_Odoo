# Configuración Específica de Odoo para `Prueba-Tecnica-Python_Odoo`
⚠️ Importante sobre la versión de Odoo

Para que esta integración funcione correctamente, es obligatorio utilizar una versión de Odoo que incluya el módulo Accounting / Contabilidad.

En Odoo Community Edition, el módulo Accounting está limitado y no permite usar todas las funcionalidades necesarias (como asientos contables completos, diarios bancarios avanzados, conciliaciones, etc.).

Por lo tanto, para esta prueba técnica se requiere:

✔️ Odoo Enterprise o Odoo Online (Business)

Estas versiones incluyen el módulo de Contabilidad Completa, necesario para:

Crear account.move

Crear account.move.line

Usar diarios de tipo cash/bank

Acceder a cuentas contables completas

Registrar pagos reales y conciliaciones

En resumen: Odoo Community no es suficiente para ejecutar esta integración. Necesitás Odoo Enterprise (local o Docker) o Odoo Business (Online).
Este documento detalla la configuración necesaria dentro de tu instancia de Odoo para que la aplicación `Prueba-Tecnica-Python_Odoo` funcione correctamente.

La aplicación interactúa con Odoo para crear asientos contables de "Pago Recibido" utilizando XML-RPC.

## 🔑 Credenciales de Acceso

La aplicación se autentica con Odoo utilizando las credenciales proporcionadas en el archivo `.env` (`ODOO_USER`, `ODOO_PASSWORD`) y se conecta a la base de datos Odoo (`ODOO_DB`). Asegúrate de que el usuario especificado tenga los permisos necesarios para:

*   Autenticarse en la base de datos de Odoo.
*   Buscar y leer `account.account` (cuentas contables).
*   Buscar y leer `account.journal` (diarios contables).
*   Crear `account.move` (asientos contables).

## 📊 Cuentas Contables Requeridas

La aplicación está configurada para utilizar códigos de cuenta específicos para las líneas de débito y crédito del asiento contable. Debes asegurarte de que estas cuentas existan en tu plan contable de Odoo:

*   **Cuenta de Débito:** Código `1.1.3.01.010` (ej. "Caja General" o similar).
*   **Cuenta de Crédito:** Código `1.1.3.01.020` (ej. "Clientes Nacionales" o similar).

Si tus códigos de cuenta son diferentes, deberás ajustar las llamadas a `odoo_service.get_account_id_by_code()` en el código fuente de la aplicación, o renombrar/crear estas cuentas en Odoo.

## 📒 Diario de Caja Requerido

La aplicación necesita un diario de tipo "Caja" (`type = 'cash'`) para registrar los movimientos. Se buscará el primer diario de caja disponible. Asegúrate de tener al menos un diario de caja configurado en Odoo.

## 📡 Acceso XML-RPC

La instancia de Odoo debe estar accesible a través de XML-RPC desde el entorno donde se ejecuta la aplicación `Prueba-Tecnica-Python_Odoo`. Esto generalmente significa que:

*   El servidor de Odoo está en ejecución y es accesible por red (IP y puerto, típicamente `8069`).
*   No hay firewalls o configuraciones de red que impidan la comunicación entre la aplicación y Odoo en el puerto `8069`.

Asegúrate de que la `ODOO_URL` en tu archivo `.env` apunte correctamente a la dirección de tu instancia de Odoo (ej. `http://localhost:8069` si Odoo se ejecuta localmente).

---

[&#x2190; Volver al README Principal](../README.md)
