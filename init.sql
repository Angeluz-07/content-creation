-- 1. Crear el usuario para Prefect
CREATE USER prefect_user WITH PASSWORD 'prefect_pass';

-- 2. Crear la base de datos asignando directamente como dueño a prefect_user
CREATE DATABASE prefect_db OWNER prefect_user;

-- 3. Por si acaso, asegurar todos los privilegios
GRANT ALL PRIVILEGES ON DATABASE prefect_db TO prefect_user;