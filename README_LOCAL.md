# Configuración y Ejecución Local de `Prueba-Tecnica-Python_Odoo`

Este documento describe cómo configurar y ejecutar la aplicación `Prueba-Tecnica-Python_Odoo` directamente en tu entorno local, sin el uso de Docker.

## 📋 Prerrequisitos

Asegúrate de tener instalados los siguientes componentes en tu sistema:

*   **Python 3.9+:** [Descargar Python](https://www.python.org/downloads/)
*   **Servidor MySQL:** [Descargar MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
*   **Pip:** El gestor de paquetes de Python (generalmente viene con Python).

## 🚀 Pasos de Configuración

### 1. Clonar el Repositorio

Si aún no lo has hecho, clona el repositorio del proyecto:

```bash
git clone [tu-url-del-repositorio]
cd Prueba-Tecnica-Python_Odoo
```

### 2. Configurar Entorno Virtual

Es una buena práctica trabajar en un entorno virtual para gestionar las dependencias del proyecto de forma aislada.

```bash
python -m venv venv
# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias de Python

Con el entorno virtual activado, instala todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos MySQL

1.  **Asegúrate de que tu servidor MySQL esté en ejecución.**
2.  **Crea una base de datos** para la aplicación. Puedes hacerlo desde la línea de comandos de MySQL o una herramienta gráfica como MySQL Workbench:
    ```sql
    CREATE DATABASE your_app_database_name;
    ```
    Reemplaza `your_app_database_name` con el nombre que desees.
3.  **Ejecuta el script de creación de tablas:**
    Navega al directorio raíz del proyecto y ejecuta el script SQL para crear la tabla `payment_events`:
    ```bash
    mysql -u your_mysql_user -p your_app_database_name < src/data/create_payment_events.sql
    ```
    Se te pedirá la contraseña de tu usuario MySQL.

### 5. Configurar Variables de Entorno (`.env`)

La aplicación requiere varias variables de entorno para conectarse a MySQL y Odoo. Crea un archivo llamado `.env` en la raíz de tu proyecto con el siguiente contenido, reemplazando los valores de marcador de posición:

```
# MySQL Database Configuration
MYSQL_HOST=127.0.0.1  # O 'localhost' si MySQL está en la misma máquina
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_app_database_name

# Odoo Connection Configuration
ODOO_URL=http://your_odoo_instance_ip_or_hostname:8069 # e.g., http://localhost:8069
ODOO_DB=your_odoo_database_name
ODOO_USER=your_odoo_username
ODOO_PASSWORD=your_odoo_password
```

### 6. Ejecutar la Aplicación FastAPI

Una vez que todas las dependencias están instaladas y las variables de entorno configuradas, puedes iniciar la aplicación:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
La opción `--reload` es útil durante el desarrollo para que los cambios en el código se reflejen automáticamente.

## ✅ Prueba la API

La aplicación estará disponible en `http://localhost:8000`. Puedes acceder a la documentación interactiva de la API en `http://localhost:8000/docs` para probar los endpoints `GET /tickets` y `POST /record-payment`.

Asegúrate de que tu instancia de Odoo esté en ejecución y sea accesible para que el endpoint `POST /record-payment` pueda completar su función de manera exitosa.

---

[&#x2190; Volver al README Principal](../README.md)
