# Docker Setup for Prueba-Tecnica-Python_Odoo

This document outlines how to set up and run the `Prueba-Tecnica-Python_Odoo` application using Docker Compose.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker:** [Install Docker Engine](https://docs.docker.com/engine/install/)
*   **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/)

## Configuration (`.env` file)

The application and the MySQL database rely on environment variables for configuration. Create a file named `.env` in the root directory of the project (where `docker-compose.yml` is located) with the following content:

```
# MySQL Database Configuration
MYSQL_ROOT_PASSWORD=your_mysql_root_password_here # For the MySQL root user (internal to Docker)
MYSQL_USER=your_app_db_user
MYSQL_PASSWORD=your_app_db_password
MYSQL_DATABASE=your_app_database_name

# Odoo Connection Configuration
ODOO_URL=http://your_odoo_instance_ip_or_hostname:8069 # e.g., http://172.17.0.1:8069 or http://localhost:8069
ODOO_DB=your_odoo_database_name
ODOO_USER=your_odoo_username
ODOO_PASSWORD=your_odoo_password
```

**Important Notes:**
*   Replace the placeholder values with your actual desired configurations.
*   The `MYSQL_HOST` for the application will be `mysql` (the service name in `docker-compose.yml`), not `localhost`, as they are on the same Docker network.
*   Ensure your Odoo instance is accessible from where Docker is running. If Odoo is also running in Docker, you might need to connect them to the same network or use appropriate Docker DNS.

## Getting Started

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone [your-repo-url]
    cd Prueba-Tecnica-Python_Odoo
    ```
2.  **Create your `.env` file** as described in the "Configuration" section above.
3.  **Build and Run the containers:**
    This command will build the Docker image for the application, create the `mysql` service, and start both containers. The `-d` flag runs them in detached mode (in the background).
    ```bash
    docker compose up --build -d
    ```
    First-time setup might take a few minutes as Docker downloads images and builds the application.

4.  **Verify container status:**
    ```bash
    docker compose ps
    ```
    You should see both `app` and `mysql` services listed as `Up`. The `mysql` service includes a healthcheck, so it might take a moment to report as healthy.

## Accessing the Application

Once the containers are running:

*   **FastAPI Application:**
    The application will be accessible at `http://localhost:8000`. You can test the endpoints using a tool like Postman, `curl`, or by navigating to `http://localhost:8000/docs` for the OpenAPI (Swagger) UI.

*   **MySQL Database:**
    The MySQL database will be accessible on port `3306` of your host machine. You can connect to it using `localhost:3306` with the credentials configured in your `.env` file.

## Database Initialization

The `mysql` service in `docker-compose.yml` includes a volume mount that will automatically execute the `src/data/create_payment_events.sql` script when the MySQL container starts for the first time. This will create the `payment_events` table.

## Stopping and Removing Containers

To stop and remove the containers, along with their networks and volumes:

```bash
docker compose down -v
```
The `-v` flag ensures that the `mysql_data` volume (which stores your database data) is also removed. Omit `-v` if you wish to keep the database data for future use.

## Troubleshooting

*   **Container fails to start:** Check the logs:
    ```bash
    docker compose logs app
    docker compose logs mysql
    ```
*   **"Address already in use" error:** Another process on your host machine is using port 8000 or 3306. Stop that process or change the port mapping in `docker-compose.yml`.
*   **Odoo connection issues:** Double-check `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, and `ODOO_PASSWORD` in your `.env` file. Ensure your Odoo instance is running and accessible from the Docker network.

---

[&#x2190; Volver al README Principal](../README.md)
