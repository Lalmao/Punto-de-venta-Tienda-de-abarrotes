import { useEffect, useState } from "react";
import { api, money } from "./api";

// tipo = "ventas" o "compras"
export default function Historial({ tipo }) {
  const [filas, setFilas] = useState([]);
  const esVenta = tipo === "ventas";

  useEffect(() => {
    api("/api/" + tipo).then(setFilas).catch(() => setFilas([]));
  }, [tipo]);

  return (
    <table>
      <thead>
        <tr>
          <th>Folio</th><th>Fecha</th>
          {esVenta ? <><th>Cliente</th><th>Empleado</th><th>Pago</th></> : <><th>Proveedor</th><th>Factura</th><th>Empleado</th></>}
          <th>Total</th>
        </tr>
      </thead>
      <tbody>
        {filas.map((f) => (
          <tr key={esVenta ? f.ID_Venta : f.ID_Compra}>
            <td>{esVenta ? f.ID_Venta : f.ID_Compra}</td>
            <td>{f.Fecha_Hora}</td>
            {esVenta
              ? <><td>{f.Cliente}</td><td>{f.Empleado}</td><td>{f.Metodo_Pago}</td></>
              : <><td>{f.Proveedor}</td><td>{f.Num_Factura}</td><td>{f.Empleado}</td></>}
            <td>${money(f.Total)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
