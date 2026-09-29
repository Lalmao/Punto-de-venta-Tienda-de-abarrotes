# Abarrotes Placencia — programa (backend + pantalla)

Programa en **Python + FastAPI** que se conecta a tu base de datos **MySQL** ya creada.
Incluye: nueva venta (con cambio y puntos de fidelidad), nueva compra, inventario con stock bajo e historiales.

## 1. Requisitos
- Python 3.10 o superior (https://www.python.org/downloads/ — marca "Add Python to PATH" al instalar)
- Tu base de datos MySQL 8 con las 9 tablas y los datos de ejemplo

## 2. Instalación (una sola vez)
Abre una terminal dentro de esta carpeta (`abarrotes`) y ejecuta:

    python -m venv venv
    venv\Scripts\activate            (Windows)
    source venv/bin/activate         (Mac / Linux)
    pip install -r requirements.txt

## 3. Conectar a tu base de datos
1. Copia `env.ejemplo` y nómbralo `.env`
2. Abre `.env` y cambia `DATABASE_URL`:

       DATABASE_URL=mysql+pymysql://USUARIO:CONTRASEÑA@localhost:3306/NOMBRE_DE_TU_BASE

   Si tu contraseña tiene caracteres raros (@, #, /) usa su versión codificada (por ejemplo @ = %40).

## 4. Ejecutar
    uvicorn app.main:app --reload

Abre en el navegador: **http://127.0.0.1:8000**
Para probar la API sin pantalla: http://127.0.0.1:8000/docs

## 5. Revisa estos 3 puntos antes de usarlo (importante)

**a) Triggers.** El documento dice que stock y totales se pueden manejar "con trigger o con la lógica de la aplicación".
Este programa lo hace con la lógica de la aplicación. En MySQL ejecuta `SHOW TRIGGERS;`
- Si sale vacío → todo bien, deja `USAR_TRIGGERS_BD=false`.
- Si tienes triggers → pon `USAR_TRIGGERS_BD=true` en `.env` (si no, el stock se descontaría dos veces).

**b) Subtotal.** El programa calcula y guarda `Subtotal` en DETALLE_VENTA y DETALLE_COMPRA.
Si en tu base esa columna es *generada* (`GENERATED ALWAYS AS ...`), MySQL rechazará el insert: avísame y lo ajustamos.

**c) AUTO_INCREMENT.** Se asume que los ID (ID_Venta, ID_Producto…) son AUTO_INCREMENT.
Y los nombres de tablas están en MAYÚSCULAS como en el documento (en Linux MySQL distingue mayúsculas).

## 6. Estructura
    app/db.py         conexión a MySQL
    app/models.py     las 9 tablas como clases
    app/schemas.py    validación de datos que llegan
    app/services.py   lógica de venta y compra (stock, totales, puntos) en una transacción
    app/main.py       rutas de la API
    app/static/index.html   la pantalla

## 7. Qué NO incluye todavía
Login por roles (JWT), reportes con gráficas/CSV, CRUD completo de empleados/proveedores/categorías desde pantalla.
Son los siguientes pasos naturales.
