import { useState } from "react";
import Pos from "./Pos.jsx";
import Inventario from "./Inventario.jsx";
import Historial from "./Historial.jsx";

const PESTANAS = [
  ["venta", "Nueva venta"],
  ["compra", "Nueva compra"],
  ["inventario", "Inventario"],
  ["ventas", "Ventas"],
  ["compras", "Compras"],
];

export default function App() {
  const [tab, setTab] = useState("venta");
  const [msg, setMsg] = useState(null);

  // Muestra un aviso verde (ok) o rojo (error) por 4 segundos
  const aviso = (texto, ok = true) => {
    setMsg({ texto, ok });
    setTimeout(() => setMsg(null), 4000);
  };

  return (
    <>
      <header>
        <h1>🛒 Abarrotes Placencia</h1>
        <nav>
          {PESTANAS.map(([id, nombre]) => (
            <button key={id} className={tab === id ? "on" : ""} onClick={() => setTab(id)}>
              {nombre}
            </button>
          ))}
        </nav>
      </header>
      <main>
        <section>
          {tab === "venta" && <Pos modo="venta" aviso={aviso} />}
          {tab === "compra" && <Pos modo="compra" aviso={aviso} />}
          {tab === "inventario" && <Inventario />}
          {tab === "ventas" && <Historial tipo="ventas" />}
          {tab === "compras" && <Historial tipo="compras" />}
        </section>
      </main>
      {msg && <div id="msg" className={msg.ok ? "ok" : "err"}>{msg.texto}</div>}
    </>
  );
}
