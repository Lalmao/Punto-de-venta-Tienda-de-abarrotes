# Actualización: Administración (respaldo, PostgreSQL y usuarios)

## 1. Copiar archivos
Copia, dentro de tu carpeta `abarrotes`, las carpetas `app` y `frontend` de este zip (acepta "Reemplazar").
No se pierde nada: tu `venv`, tu `.env` y `node_modules` no se tocan.

## 2. Instalar lo nuevo (una vez)
Con el entorno activado `(venv)`, en la carpeta `abarrotes`:

    pip install -r requirements.txt

(solo agrega `psycopg2-binary`, el conector de PostgreSQL). En el frontend no hay nada nuevo que instalar.

## 3. Agregar al .env
Abre `env.ejemplo`, copia las líneas nuevas a tu `.env` y cambia contraseñas:
ADMIN_KEY, ADMIN_DATABASE_URL y PG_DATABASE_URL.
Como tu base tiene 6 triggers, deja `USAR_TRIGGERS_BD=true`.

## 4. Reiniciar y entrar
Reinicia el backend (Ctrl+C y otra vez `uvicorn app.main:app --reload`), abre http://localhost:5173
y entra a la pestaña **⚙ Administración** con tu ADMIN_KEY.
Arriba verás una lista con ✔/✖ de qué está conectado y qué herramientas encontró (mysqldump, mysql, pg_dump, psql).

## Si una herramienta sale con ✖
Agrega su carpeta al .env, por ejemplo:

    MYSQL_BIN_DIR=C:\Program Files\MySQL\MySQL Server 8.0\bin
    PG_BIN_DIR=C:\Program Files\PostgreSQL\18\bin

## Seguridad
- Todo el panel exige la ADMIN_KEY. Sin ella, ni el backend responde.
- Las contraseñas no se escriben en la línea de comandos ni en la bitácora.
- Cada acción queda en `respaldos/auditoria.log`.
- No expongas este servidor a internet: es para uso local.
