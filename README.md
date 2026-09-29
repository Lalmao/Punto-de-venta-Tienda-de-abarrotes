# Punto-de-venta-Tienda-de-abarrotes
</head><body>
<h1>Abarrotes Placencia: Requerimientos y diseño de software</h1>
<p>Sistema de control de inventario, ventas y compras. Basado en el modelo relacional de 9 tablas (CATEGORIA, PROVEEDOR, PRODUCTO, CLIENTE, EMPLEADO, VENTA, DETALLE_VENTA, COMPRA, DETALLE_COMPRA).</p>
<h2>1. Supuestos y decisiones (revisa y cambia lo que no te convenga)</h2>
<table>
<thead>
<tr>
<th>#</th>
<th>Decisión</th>
<th>Motivo</th>
</tr>
</thead>
<tbody>
<tr>
<td>D1</td>
<td><strong>MySQL 8</strong> (usa ENUM y columnas generadas)</td>
<td>El modelo ya está en ese dialecto</td>
</tr>
<tr>
<td>D2</td>
<td><strong>Backend: Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2</strong></td>
<td>Validación integrada, documentación automática (<code>/docs</code>), ORM con llaves compuestas y transacciones</td>
</tr>
<tr>
<td>D3</td>
<td><strong>Frontend: React + Vite + TypeScript</strong>, TanStack Query (datos) y React Router</td>
<td>Pantalla de caja rápida; el frontend consume la API vía JSON</td>
</tr>
<tr>
<td>D4</td>
<td><strong>Totales y stock se manejan en la capa de servicio, dentro de una transacción. No se usan triggers</strong></td>
<td>Evita que el stock se descuente dos veces (trigger + app) y es más fácil de probar</td>
</tr>
<tr>
<td>D5</td>
<td>Subtotal = <strong>columna generada</strong> (<code>Cantidad * Precio_Unitario</code>)</td>
<td>Elimina inconsistencias</td>
</tr>
<tr>
<td>D6</td>
<td>Autenticación con login por empleado (JWT) y 3 roles: ADMIN, ENCARGADO, CAJERO</td>
<td>El enunciado no define usuarios; se necesitan para saber quién atiende</td>
</tr>
<tr>
<td>D7</td>
<td>Puntos de fidelidad: <strong>1 punto por cada $10 de compra</strong> (configurable)</td>
<td>El enunciado no define la regla</td>
</tr>
<tr>
<td>D8</td>
<td>Un producto <strong>no puede repetirse</strong> en una misma venta o compra (PK compuesta). Si se agrega dos veces, se suman las cantidades</td>
<td>Consecuencia de la PK (ID_Venta, ID_Producto)</td>
</tr>
<tr>
<td>D9</td>
<td>Cambios al modelo: <code>UNIQUE(ID_Proveedor, Num_Factura)</code> en COMPRA y tabla <code>USUARIO</code> (ver sección 6)</td>
<td>El propio documento dice que el número de factura puede repetirse entre proveedores</td>
</tr>
</tbody>
</table>
<h2>2. Alcance</h2>
<p><strong>Incluye:</strong> catálogos (categorías, productos, proveedores, empleados, clientes), punto de venta, registro de compras a proveedores, control de stock, programa de fidelidad y reportes básicos.</p>
<p><strong>No incluye (v1):</strong> facturación fiscal (CFDI), cancelaciones/devoluciones, cortes de caja, e-commerce, multi-sucursal.</p>
<h2>3. Roles</h2>
<table>
<thead>
<tr>
<th>Rol</th>
<th>Puede hacer</th>
</tr>
</thead>
<tbody>
<tr>
<td>CAJERO</td>
<td>Registrar ventas, consultar productos y clientes, alta de clientes</td>
</tr>
<tr>
<td>ENCARGADO</td>
<td>Todo lo del cajero + compras, catálogos de productos/categorías/proveedores, reportes</td>
</tr>
<tr>
<td>ADMIN</td>
<td>Todo + empleados y usuarios, configuración</td>
</tr>
</tbody>
</table>
<h2>4. Requerimientos funcionales</h2>
<h3>Catálogos</h3>
<ul>
<li><strong>RF-01</strong> CRUD de categorías (nombre, descripción, activo).</li>
<li><strong>RF-02</strong> CRUD de productos con nombre, descripción, precio de costo, precio de venta, stock, activo, categoría (obligatoria) y proveedor (opcional).</li>
<li><strong>RF-03</strong> CRUD de proveedores (RFC/NIF único, empresa, teléfono, contacto, activo).</li>
<li><strong>RF-04</strong> CRUD de empleados (nombre, cargo, turno MATUTINO/VESPERTINO/NOCTURNO, activo).</li>
<li><strong>RF-05</strong> CRUD de clientes (nombre, teléfono, puntos, fecha de registro automática, activo).</li>
<li><strong>RF-06</strong> Borrado <strong>lógico</strong> (<code>Activo = false</code>) en todos los catálogos. No hay DELETE físico desde la interfaz.</li>
<li><strong>RF-07</strong> Búsqueda y filtros: producto por nombre/categoría/proveedor/activo; cliente por nombre o teléfono.</li>
</ul>
<h3>Ventas</h3>
<ul>
<li><strong>RF-08</strong> Crear venta: el empleado autenticado queda como atendedor; cliente opcional (NULL = público general); método de pago EFECTIVO, TARJETA_DEBITO, TARJETA_CREDITO o TRANSFERENCIA.</li>
<li><strong>RF-09</strong> Agregar líneas por producto con cantidad. El precio unitario se copia de <code>Precio_Venta</code> en ese instante.</li>
<li><strong>RF-10</strong> Calcular subtotal por línea y total de la venta automáticamente.</li>
<li><strong>RF-11</strong> Descontar stock por cada línea. Rechazar la venta completa si algún producto no tiene stock suficiente.</li>
<li><strong>RF-12</strong> Solo se pueden vender productos activos.</li>
<li><strong>RF-13</strong> Si hay cliente, sumar puntos de fidelidad (regla D7).</li>
<li><strong>RF-14</strong> Consultar historial de ventas por fecha, empleado, cliente y método de pago, con detalle y ticket imprimible.</li>
<li><strong>RF-15</strong> En efectivo, capturar monto recibido y mostrar cambio (no se guarda en BD).</li>
</ul>
<h3>Compras</h3>
<ul>
<li><strong>RF-16</strong> Crear compra: proveedor (obligatorio, activo), número de factura, empleado autenticado, fecha automática.</li>
<li><strong>RF-17</strong> Agregar líneas con producto, cantidad y costo unitario capturado. La compra puede incluir productos de otro proveedor o sin proveedor.</li>
<li><strong>RF-18</strong> Total calculado como suma de subtotales.</li>
<li><strong>RF-19</strong> Incrementar stock por cada línea y, opcionalmente, actualizar <code>Precio_Costo</code> del producto con el último costo (casilla en pantalla).</li>
<li><strong>RF-20</strong> Consultar historial de compras con filtros por proveedor, fecha y factura.</li>
</ul>
<h3>Inventario y reportes</h3>
<ul>
<li><strong>RF-21</strong> Alerta de stock bajo (umbral configurable, por defecto 10).</li>
<li><strong>RF-22</strong> Reportes: ventas del día/rango, productos más vendidos, ventas por empleado, compras por proveedor, utilidad estimada (<code>Precio_Unitario - Precio_Costo</code>), clientes con más puntos.</li>
<li><strong>RF-23</strong> Exportar reportes a CSV.</li>
</ul>
<h3>Seguridad</h3>
<ul>
<li><strong>RF-24</strong> Login, cierre de sesión y control de acceso por rol.</li>
</ul>
<h2>5. Reglas de negocio</h2>
<table>
<thead>
<tr>
<th>ID</th>
<th>Regla</th>
</tr>
</thead>
<tbody>
<tr>
<td>RN-01</td>
<td>Toda venta tiene exactamente un empleado y toda compra un proveedor y un empleado</td>
</tr>
<tr>
<td>RN-02</td>
<td><code>Precio_Unitario</code> y <code>Costo_Unitario</code> son un histórico: nunca se recalculan si cambia el producto</td>
</tr>
<tr>
<td>RN-03</td>
<td><code>Venta.Total = Σ(Cantidad × Precio_Unitario)</code>; <code>Compra.Total = Σ(Cantidad × Costo_Unitario)</code></td>
</tr>
<tr>
<td>RN-04</td>
<td>Stock nunca negativo (<code>CHECK Stock_Actual &gt;= 0</code>)</td>
</tr>
<tr>
<td>RN-05</td>
<td>Un producto con historial no se elimina físicamente (FK RESTRICT); solo se desactiva</td>
</tr>
<tr>
<td>RN-06</td>
<td>Un empleado inactivo no puede iniciar sesión, pero sus ventas y compras se conservan</td>
</tr>
<tr>
<td>RN-07</td>
<td>Al desactivar un proveedor, sus productos conservan la referencia (solo se oculta en nuevas compras)</td>
</tr>
<tr>
<td>RN-08</td>
<td>Cantidad &gt; 0; precios y costos ≥ 0</td>
</tr>
<tr>
<td>RN-09</td>
<td>Ventas y compras son inmutables una vez registradas (v1 no permite editar ni cancelar; ver mejoras)</td>
</tr>
</tbody>
</table>
<h2>6. Ajustes recomendados al modelo de datos</h2>
<ol>
<li><code>COMPRA</code>: agregar <code>UNIQUE (ID_Proveedor, Num_Factura)</code>.</li>
<li><code>DETALLE_VENTA.Subtotal</code> y <code>DETALLE_COMPRA.Subtotal</code> como <code>DECIMAL(10,2) GENERATED ALWAYS AS (Cantidad * Precio_Unitario) STORED</code> (o <code>Costo_Unitario</code>).</li>
<li><code>CHECK</code> en: <code>Cantidad &gt; 0</code>, precios/costos ≥ 0, <code>Stock_Actual &gt;= 0</code>, <code>Puntos_Fidelidad &gt;= 0</code>.</li>
<li>Índices: <code>PRODUCTO(Nombre)</code>, <code>PRODUCTO(ID_Categoria)</code>, <code>VENTA(Fecha_Hora)</code>, <code>COMPRA(Fecha_Hora)</code>, <code>CLIENTE(Telefono)</code>.</li>
<li>Nueva tabla de autenticación (relación 1:1 con EMPLEADO):</li>
</ol>
<pre><code class="language-sql">CREATE TABLE USUARIO (
  ID_Empleado   INT PRIMARY KEY,
  Username      VARCHAR(50) UNIQUE NOT NULL,
  Password_Hash VARCHAR(255) NOT NULL,
  Rol           ENUM(&#39;ADMIN&#39;,&#39;ENCARGADO&#39;,&#39;CAJERO&#39;) NOT NULL,
  FOREIGN KEY (ID_Empleado) REFERENCES EMPLEADO(ID_Empleado)
);
</code></pre>
<ol start="6">
<li>Tabla opcional <code>CONFIGURACION(Clave, Valor)</code> para umbral de stock bajo y pesos por punto.</li>
</ol>
<h2>7. Requerimientos no funcionales</h2>
<table>
<thead>
<tr>
<th>ID</th>
<th>Requerimiento</th>
</tr>
</thead>
<tbody>
<tr>
<td>RNF-01</td>
<td>Registrar una venta de hasta 10 líneas en menos de 1 segundo (servidor)</td>
</tr>
<tr>
<td>RNF-02</td>
<td>Consistencia ACID: venta/compra + líneas + stock + puntos en <strong>una sola transacción</strong></td>
</tr>
<tr>
<td>RNF-03</td>
<td>Contraseñas con bcrypt; JWT con expiración de 8 h</td>
</tr>
<tr>
<td>RNF-04</td>
<td>Validación en frontend y backend (esquemas Pydantic; el frontend valida con Zod o react-hook-form)</td>
</tr>
<tr>
<td>RNF-05</td>
<td>Interfaz utilizable con teclado y lector de código de barras en caja</td>
</tr>
<tr>
<td>RNF-06</td>
<td>Respaldos diarios de la base (mysqldump programado)</td>
</tr>
<tr>
<td>RNF-07</td>
<td>Cobertura de pruebas ≥ 70 % en la capa de servicios (pytest + httpx; Vitest en el frontend)</td>
</tr>
<tr>
<td>RNF-08</td>
<td>Bitácora de errores y de operaciones críticas (venta, compra)</td>
</tr>
</tbody>
</table>
<h2>8. Casos de uso principales</h2>
<p><strong>CU-01 Registrar venta</strong> (Cajero)</p>
<ol>
<li>El cajero abre &quot;Nueva venta&quot;. Opcional: busca cliente por teléfono.</li>
<li>Escanea/busca productos y ajusta cantidades. El sistema muestra subtotales y total.</li>
<li>Elige método de pago y confirma.</li>
<li>El sistema valida (productos activos, stock), guarda todo en una transacción y muestra el ticket.</li>
</ol>
<ul>
<li><em>Alterno:</em> stock insuficiente → mensaje indicando el producto y la existencia; no se guarda nada.</li>
</ul>
<p><strong>CU-02 Registrar compra</strong> (Encargado)</p>
<ol>
<li>Selecciona proveedor y captura el número de factura.</li>
<li>Agrega productos con cantidad y costo unitario.</li>
<li>Confirma; el sistema guarda, suma stock y (si se marcó) actualiza <code>Precio_Costo</code>.</li>
</ol>
<ul>
<li><em>Alterno:</em> factura repetida para el mismo proveedor → error.</li>
</ul>
<p><strong>CU-03 Gestionar catálogos</strong> (Encargado/Admin): alta, edición y desactivación con confirmación.</p>
<p><strong>CU-04 Consultar reportes</strong> (Encargado/Admin).</p>
<h2>9. Arquitectura</h2>
<pre><code>[React SPA] --HTTPS/JSON--&gt; [FastAPI] --&gt; [Services] --&gt; [SQLAlchemy] --&gt; [MySQL 8]
                               |              |
                          JWT/roles      Transacciones
                        (Depends)      (venta, compra)
</code></pre>
<p>Capas del backend: <strong>routers → services → models (SQLAlchemy)</strong>, con <strong>schemas (Pydantic)</strong> para entrada y salida. Toda la lógica de negocio (stock, totales, puntos) vive en <code>services</code>; los routers solo validan, autorizan y delegan.</p>
<h3>Estructura de carpetas</h3>
<pre><code>abarrotes/
├─ backend/
│  ├─ alembic/            (migraciones)
│  ├─ app/
│  │  ├─ main.py          (instancia FastAPI, CORS, routers)
│  │  ├─ core/            (config, security.py con JWT y bcrypt, deps.py)
│  │  ├─ db/              (session.py, base.py)
│  │  ├─ models/          (categoria, proveedor, producto, cliente, empleado,
│  │  │                    usuario, venta, detalle_venta, compra, detalle_compra)
│  │  ├─ schemas/         (un archivo Pydantic por recurso)
│  │  ├─ services/        (venta_service, compra_service, reporte_service, ...)
│  │  └─ routers/         (auth, categorias, productos, proveedores, empleados,
│  │                       clientes, ventas, compras, reportes)
│  ├─ tests/
│  ├─ seed.py             (datos de ejemplo del documento)
│  └─ requirements.txt
├─ frontend/
│  └─ src/ (pages, components, hooks, api, store, routes)
└─ docs/
</code></pre>
<p>Puntos específicos de FastAPI:</p>
<ul>
<li><code>get_db()</code> como dependencia que entrega una sesión por petición.</li>
<li><code>require_role(&quot;ENCARGADO&quot;, &quot;ADMIN&quot;)</code> como dependencia reutilizable para controlar roles.</li>
<li>Enums de Python (<code>Turno</code>, <code>MetodoPago</code>, <code>Rol</code>) compartidos entre modelos y schemas.</li>
<li>Documentación interactiva automática en <code>/docs</code> (Swagger), útil para probar sin frontend.</li>
<li>CORS habilitado solo para el origen del frontend.</li>
<li>Nota: SQLAlchemy es síncrono por defecto con el driver <code>pymysql</code>; para este volumen es suficiente y más simple que <code>async</code>. Los endpoints se declaran con <code>def</code> (no <code>async def</code>) para que FastAPI los ejecute en un pool de hilos.</li>
</ul>
<h2>10. Diseño de la API REST (<code>/api/v1</code>)</h2>
<table>
<thead>
<tr>
<th>Recurso</th>
<th>Endpoints</th>
<th>Roles</th>
</tr>
</thead>
<tbody>
<tr>
<td>Auth</td>
<td><code>POST /auth/login</code>, <code>GET /auth/me</code></td>
<td>todos</td>
</tr>
<tr>
<td>Categorías</td>
<td><code>GET/POST /categorias</code>, <code>GET/PUT /categorias/:id</code>, <code>PATCH /categorias/:id/estado</code></td>
<td>lectura todos; escritura ENCARGADO+</td>
</tr>
<tr>
<td>Productos</td>
<td><code>GET/POST /productos</code>, <code>GET/PUT /productos/:id</code>, <code>PATCH /productos/:id/estado</code>, <code>GET /productos/stock-bajo</code></td>
<td>igual</td>
</tr>
<tr>
<td>Proveedores</td>
<td>mismo patrón que categorías</td>
<td>ENCARGADO+</td>
</tr>
<tr>
<td>Empleados</td>
<td>mismo patrón</td>
<td>ADMIN</td>
</tr>
<tr>
<td>Clientes</td>
<td>mismo patrón + <code>GET /clientes?tel=</code></td>
<td>CAJERO+</td>
</tr>
<tr>
<td>Ventas</td>
<td><code>POST /ventas</code>, <code>GET /ventas</code>, <code>GET /ventas/:id</code></td>
<td>CAJERO+</td>
</tr>
<tr>
<td>Compras</td>
<td><code>POST /compras</code>, <code>GET /compras</code>, <code>GET /compras/:id</code></td>
<td>ENCARGADO+</td>
</tr>
<tr>
<td>Reportes</td>
<td><code>GET /reportes/ventas</code>, <code>/top-productos</code>, <code>/utilidad</code>, <code>/compras-proveedor</code></td>
<td>ENCARGADO+</td>
</tr>
</tbody>
</table>
<p><strong>Ejemplo <code>POST /ventas</code></strong></p>
<pre><code class="language-json">{
  &#34;idCliente&#34;: 1,
  &#34;metodoPago&#34;: &#34;EFECTIVO&#34;,
  &#34;lineas&#34;: [
    { &#34;idProducto&#34;: 1, &#34;cantidad&#34;: 2 },
    { &#34;idProducto&#34;: 6, &#34;cantidad&#34;: 3 }
  ]
}
</code></pre>
<p>El servidor toma <code>ID_Empleado</code> del token (<code>Depends(get_current_user)</code>) y el precio de <code>Precio_Venta</code>. El cliente <strong>nunca</strong> envía precios ni totales.</p>
<p><strong>Ejemplo <code>POST /compras</code></strong></p>
<pre><code class="language-json">{
  &#34;idProveedor&#34;: 3,
  &#34;numFactura&#34;: &#34;CCF-000451&#34;,
  &#34;actualizarCosto&#34;: true,
  &#34;lineas&#34;: [ { &#34;idProducto&#34;: 1, &#34;cantidad&#34;: 120, &#34;costoUnitario&#34;: 12.00 } ]
}
</code></pre>
<p>Errores estándar: <code>400</code> validación, <code>401/403</code> auth, <code>404</code> no existe, <code>409</code> conflicto (RFC o factura duplicada, stock insuficiente).</p>
<h2>11. Lógica clave (pseudocódigo)</h2>
<p><strong>crearVenta(usuario, dto)</strong></p>
<pre><code>transacción:
  agrupar líneas repetidas por idProducto (sumar cantidad)
  si dto.idCliente: validar cliente activo
  total = 0
  para cada línea (ordenadas por idProducto, para evitar deadlocks):
     producto = db.query(Producto).filter_by(id=x).with_for_update().one()
     validar producto.activo
     validar producto.stock &gt;= cantidad          -&gt; 409 si no
     precio = producto.precioVenta
     insertar DETALLE_VENTA(idVenta, idProducto, cantidad, precio)
     producto.stock -= cantidad
     total += cantidad * precio
  crear VENTA con total, empleado = usuario.idEmpleado
  si cliente: puntos += floor(total / 10)
commit
</code></pre>
<p><strong>crearCompra(usuario, dto)</strong>: igual, pero valida proveedor activo y factura única, suma stock, guarda <code>Costo_Unitario</code> y, si <code>actualizarCosto</code>, actualiza <code>Precio_Costo</code>.</p>
<p>Como Total va en la fila padre, primero se insertan las líneas en memoria y se calcula el total; luego se inserta la cabecera y las líneas dentro de la misma transacción.</p>
<h2>12. Pantallas (frontend)</h2>
<ol>
<li>Login</li>
<li><strong>Punto de venta</strong> (pantalla principal): buscador de producto, tabla de líneas, cliente, método de pago, total grande, botón Cobrar</li>
<li>Historial de ventas + detalle/ticket</li>
<li>Compras: formulario y historial</li>
<li>Productos (lista con filtros, formulario, indicador de stock bajo)</li>
<li>Categorías, Proveedores, Clientes, Empleados (tabla + formulario modal)</li>
<li>Reportes con gráficas y exportar CSV</li>
<li>Dashboard: ventas de hoy, stock bajo, top 5 productos</li>
</ol>
<h2>13. Plan de desarrollo (orden sugerido)</h2>
<table>
<thead>
<tr>
<th>Sprint</th>
<th>Entregable</th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Repositorio, entorno virtual, MySQL, modelos SQLAlchemy, migración inicial con Alembic, <code>seed.py</code> con los datos de ejemplo del documento</td>
</tr>
<tr>
<td>2</td>
<td>Auth (JWT) + dependencias de roles; CRUD de categorías, proveedores, empleados</td>
</tr>
<tr>
<td>3</td>
<td>CRUD de productos y clientes; búsqueda y filtros</td>
</tr>
<tr>
<td>4</td>
<td><strong>Ventas</strong> (servicio transaccional + pruebas) y pantalla de caja</td>
</tr>
<tr>
<td>5</td>
<td><strong>Compras</strong> y actualización de inventario</td>
</tr>
<tr>
<td>6</td>
<td>Reportes, dashboard, exportación CSV</td>
</tr>
<tr>
<td>7</td>
<td>Pruebas de integración, pulido, respaldos, despliegue</td>
</tr>
</tbody>
</table>
<h2>14. Pruebas mínimas</h2>
<ul>
<li>Venta con stock suficiente: baja stock y <code>Total</code> coincide con la suma de subtotales.</li>
<li>Venta con un producto sin stock: no se guarda nada (rollback completo).</li>
<li>Venta con producto inactivo: rechazada.</li>
<li>Venta sin cliente: <code>ID_Cliente = NULL</code>, no suma puntos.</li>
<li>Dos ventas simultáneas del último producto: solo una tiene éxito.</li>
<li>Compra: sube stock; misma factura del mismo proveedor: 409; misma factura de otro proveedor: permitida.</li>
<li>Cambiar <code>Precio_Venta</code> no altera ventas pasadas.</li>
<li>RFC duplicado: 409. Cajero intentando crear compra: 403.</li>
</ul>
<h2>15. Mejoras futuras</h2>
<p>Cancelación y devoluciones con movimientos inversos de stock, corte de caja, tabla <code>MOVIMIENTO_INVENTARIO</code> para auditoría, canje de puntos, códigos de barras por producto, facturación CFDI.</p>

</body></html>
