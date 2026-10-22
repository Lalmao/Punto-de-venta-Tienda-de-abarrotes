import { useEffect, useState } from "react";
import { api, money } from "./api";

export default function Inventario() {
  const [q, setQ] = useState("");
  const [soloBajo, setSoloBajo] = useState(false);
  const [filas, setFilas] = useState([]);

  // Se vuelve a consultar cada vez que cambia la búsqueda o la casilla
  useEffect(() => {
    const url = soloBajo ? "/api/productos/stock-bajo" : "/api/productos?q=" + encodeURIComponent(q);
    api(url).then(setFilas).catch(() => setFilas([]));
  }, [q, soloBajo]);

  return (
    <>
      <div className="row">
        <input placeholder="Buscar…" value={q} onChange={(e) => setQ(e.target.value)} />
        <label style={{ flexDirection: "row", alignItems: "center" }}>
          <input type="checkbox" checked={soloBajo} onChange={(e) => setSoloBajo(e.target.checked)} /> Solo stock bajo (≤ 10)
        </label>
      </div>
      <table>
        <thead><tr><th>ID</th><th>Producto</th><th>Categoría</th><th>Costo</th><th>Venta</th><th>Stock</th></tr></thead>
        <tbody>
          {filas.map((p) => (
            <tr key={p.ID_Producto}>
              <td>{p.ID_Producto}</td><td>{p.Nombre}</td><td>{p.Categoria}</td>
              <td>${money(p.Precio_Costo)}</td><td>${money(p.Precio_Venta)}</td>
              <td className={p.Stock_Actual <= 10 ? "bajo" : ""}>{p.Stock_Actual}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
