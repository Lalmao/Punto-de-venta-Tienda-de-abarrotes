import { useEffect, useState } from "react";
import { api, post, money } from "./api";

// Este componente sirve para VENTA y para COMPRA (cambia con la prop "modo")
export default function Pos({ modo, aviso }) {
  const esVenta = modo === "venta";

  // Datos que vienen de la base de datos
  const [catalogo, setCatalogo] = useState([]);
  const [empleados, setEmpleados] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [proveedores, setProveedores] = useState([]);

  // Lo que el usuario captura
  const [empleado, setEmpleado] = useState("");
  const [cliente, setCliente] = useState("");
  const [pago, setPago] = useState("EFECTIVO");
  const [proveedor, setProveedor] = useState("");
  const [factura, setFactura] = useState("");
  const [actualizarCosto, setActualizarCosto] = useState(false);
  const [recibido, setRecibido] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [lineas, setLineas] = useState([]);

  async function cargar() {
    const [emps, clis, provs, prods] = await Promise.all([
      api("/api/empleados"), api("/api/clientes"), api("/api/proveedores"), api("/api/productos"),
    ]);
    setEmpleados(emps); setClientes(clis); setProveedores(provs); setCatalogo(prods);
    setEmpleado((actual) => actual || emps[0]?.ID_Empleado || "");
    setProveedor((actual) => actual || provs[0]?.ID_Proveedor || "");
  }

  useEffect(() => {
    cargar().catch((e) => aviso("No se pudo conectar: " + e.message, false));
  }, []);

  const resultados = busqueda.trim()
    ? catalogo.filter((p) => p.Nombre.toLowerCase().includes(busqueda.trim().toLowerCase())).slice(0, 8)
    : [];

  function agregar(p) {
    setLineas((ls) =>
      ls.some((l) => l.id === p.ID_Producto)
        ? ls.map((l) => (l.id === p.ID_Producto ? { ...l, cantidad: l.cantidad + 1 } : l))
        : [...ls, { id: p.ID_Producto, nombre: p.Nombre, cantidad: 1,
                    precio: esVenta ? p.Precio_Venta : p.Precio_Costo }]
    );
    setBusqueda("");
  }

  const cambiar = (id, campo, valor) =>
    setLineas((ls) => ls.map((l) => (l.id === id ? { ...l, [campo]: Number(valor) } : l)));
  const quitar = (id) => setLineas((ls) => ls.filter((l) => l.id !== id));

  const total = lineas.reduce((s, l) => s + l.cantidad * l.precio, 0);
  const cambio = Math.max(Number(recibido || 0) - total, 0);

  async function guardar() {
    try {
      if (esVenta) {
        const r = await post("/api/ventas", {
          idEmpleado: Number(empleado),
          idCliente: cliente ? Number(cliente) : null,
          metodoPago: pago,
          lineas: lineas.map((l) => ({ idProducto: l.id, cantidad: l.cantidad })),
        });
        aviso(`Venta #${r.idVenta} guardada. Total $${money(r.total)}` +
              (r.puntosGanados ? ` (+${r.puntosGanados} puntos)` : ""));
      } else {
        const r = await post("/api/compras", {
          idProveedor: Number(proveedor), idEmpleado: Number(empleado),
          numFactura: factura.trim(), actualizarCosto,
          lineas: lineas.map((l) => ({ idProducto: l.id, cantidad: l.cantidad, costoUnitario: l.precio })),
        });
        aviso(`Compra #${r.idCompra} guardada. Total $${money(r.total)}`);
      }
      setLineas([]); setRecibido(""); setFactura("");
      await cargar(); // refresca el stock
    } catch (e) {
      aviso(e.message, false);
    }
  }

  return (
    <>
      <div className="row">
        <label>
          {esVenta ? "Empleado que atiende" : "Empleado que registra"}
          <select value={empleado} onChange={(e) => setEmpleado(e.target.value)}>
            {empleados.map((e) => <option key={e.ID_Empleado} value={e.ID_Empleado}>{e.Nombre}</option>)}
          </select>
        </label>

        {esVenta ? (
          <>
            <label>
              Cliente (opcional)
              <select value={cliente} onChange={(e) => setCliente(e.target.value)}>
                <option value="">Público general</option>
                {clientes.map((c) => <option key={c.ID_Cliente} value={c.ID_Cliente}>{c.Nombre}</option>)}
              </select>
            </label>
            <label>
              Método de pago
              <select value={pago} onChange={(e) => setPago(e.target.value)}>
                {["EFECTIVO", "TARJETA_DEBITO", "TARJETA_CREDITO", "TRANSFERENCIA"].map((m) => <option key={m}>{m}</option>)}
              </select>
            </label>
          </>
        ) : (
          <>
            <label>
              Proveedor
              <select value={proveedor} onChange={(e) => setProveedor(e.target.value)}>
                {proveedores.map((p) => <option key={p.ID_Proveedor} value={p.ID_Proveedor}>{p.Nombre_Empresa}</option>)}
              </select>
            </label>
            <label>
              Núm. de factura
              <input value={factura} maxLength={30} onChange={(e) => setFactura(e.target.value)} />
            </label>
            <label style={{ justifyContent: "flex-end" }}>
              <span>
                <input type="checkbox" checked={actualizarCosto} onChange={(e) => setActualizarCosto(e.target.checked)} />{" "}
                Actualizar precio de costo
              </span>
            </label>
          </>
        )}
      </div>

      <input className="buscar" placeholder="Buscar producto por nombre…" value={busqueda}
             onChange={(e) => setBusqueda(e.target.value)} />
      <div>
        {resultados.map((p) => (
          <button key={p.ID_Producto} className="btn sec chip" onClick={() => agregar(p)}>
            {p.Nombre} (stock {p.Stock_Actual})
          </button>
        ))}
      </div>

      <table>
        <thead>
          <tr><th>Producto</th><th>Cantidad</th><th>{esVenta ? "Precio" : "Costo unit."}</th><th>Subtotal</th><th></th></tr>
        </thead>
        <tbody>
          {lineas.map((l) => (
            <tr key={l.id}>
              <td>{l.nombre}</td>
              <td><input type="number" min="1" value={l.cantidad} onChange={(e) => cambiar(l.id, "cantidad", e.target.value)} /></td>
              <td>
                {esVenta ? `$${money(l.precio)}` : (
                  <input type="number" min="0" step="0.01" value={l.precio} onChange={(e) => cambiar(l.id, "precio", e.target.value)} />
                )}
              </td>
              <td>${money(l.cantidad * l.precio)}</td>
              <td><button className="btn sec" onClick={() => quitar(l.id)}>✕</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="total">Total: ${money(total)}</div>

      {esVenta && pago === "EFECTIVO" && (
        <div className="row">
          <label>Recibido
            <input type="number" min="0" step="0.5" value={recibido} onChange={(e) => setRecibido(e.target.value)} />
          </label>
          <label>Cambio <b style={{ fontSize: 20 }}>${money(cambio)}</b></label>
        </div>
      )}

      <button className="btn" onClick={guardar} disabled={lineas.length === 0}>
        {esVenta ? "Cobrar" : "Registrar compra"}
      </button>
    </>
  );
}
