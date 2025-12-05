# Prueba Técnica — FastAPI • MySQL • Odoo (Registro de Pago)

Esta prueba técnica consiste en desarrollar un microservicio con **FastAPI**, usando **MySQL** como base de datos local y **Odoo** como sistema contable externo.

## 🎯 Objetivo del Sistema
El servicio debe recibir un evento de **"Pago Recibido"** y ejecutar tres acciones:

1. **Registrar en Odoo** un asiento contable (`account.move`) con:
   - Línea de Débito → Cuenta **1105 (Caja General)**
   - Línea de Crédito → Cuenta **4105 (Clientes Nacionales)**

2. **Guardar localmente en MySQL** un evento en la tabla `payment_events` con:
   - Monto del pago
   - Fecha del evento
   - Estado de sincronización (`PENDING`, `COMPLETED`, `FAILED`)
   - ID del movimiento generado en Odoo (si existe)

3. **Actualizar el estado** según el resultado:
   - `COMPLETED` si Odoo responde correctamente
   - `FAILED` si ocurre un error en la API de Odoo

---

## 🗃 Tabla MySQL Requerida (`payment_events`)

La prueba exige una tabla minimalista con:

- `event_id` (INT, PK, AUTO_INCREMENT)
- `amount` (DECIMAL)
- `event_date` (DATETIME)
- `odoo_move_id` (INT, NULLABLE)
- `sync_status` (ENUM: `PENDING`, `COMPLETED`, `FAILED`)

El repositorio incluye el archivo SQL para crearla.

---

## 📌 Endpoint Solicitado

### `POST /record-payment`

Debe recibir un JSON con:

```json
{
  "amount": 123.45,
  "date": "2025-01-15T12:00:00"
}

Y ejecutar todo el flujo:

Guardar evento como PENDING

Enviar asiento contable a Odoo mediante XML-RPC

Actualizar estado y guardar odoo_move_id

📦 Entregables Requeridos

El repositorio incluye:

✔ Script SQL con la creación de payment_events
✔ Código FastAPI con el endpoint /record-payment
✔ Lógica para conectar a Odoo (XML-RPC)
✔ Lógica para registrar y actualizar el evento en MySQL
✔ Documentación de cuentas requeridas en Odoo
✔ Instrucciones para ejecutar pruebas y verificar resultados