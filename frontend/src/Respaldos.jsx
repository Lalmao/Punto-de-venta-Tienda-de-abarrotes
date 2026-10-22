import { useEffect, useState } from "react";
import { api, post, del, descargar } from "./api";

export default function Respaldos({ aviso }) {
  const [motor, setMotor] = useState("mysql");
  const [lista, setLista] = useState([]);
  const [ocupado, setOcupado] = useState(false);

  const cargar = () => api("/api/admin/respaldos").then(setLista).catch((e) => aviso(e.message, false));
  useEffect(() => { cargar(); }, []);

  async function crear() {
    setOcupado(true);
    try {
      const r = await post("/api/admin/respaldos", { motor });
      aviso(`Respaldo ${r.nombre} creado (${r.kb} KB, ${r.tablas} tablas, ${r.triggers} triggers)`);
      await cargar();
    } catch (e) { aviso(e.message, false); }
    setOcupado(false);
  }

  async function restaurar(a) {
    const motorTxt = a.motor === "mysql" ? "MySQL" : "PostgreSQL";
    const resp = window.prompt(
      `Se REEMPLAZARÁN los datos actuales de ${motorTxt} con "${a.nombre}".\n` +
      `Antes se hará un respaldo de seguridad automático.\n\nEscribe RESTAURAR para confirmar:`);
    if (resp !== "RESTAURAR") return;
    setOcupado(true);
    try {
      const r = await post("/api/admin/respaldos/restaurar", { archivo: a.nombre, confirmacion: resp });
      aviso(`Restauración lista. Seguridad previa: ${r.respaldo_de_seguridad}`);
      await cargar();
    } catch (e) { aviso(e.message, false); }
    setOcupado(false);
  }

  async function eliminar(a) {
    if (!window.confirm(`¿Eliminar ${a.nombre}?`)) return;
    try { await del(`/api/admin/respaldos/${a.nombre}`); await cargar(); } catch (e) { aviso(e.message, false); }
  }

  return (
    <>
      <div className="row" style={{ alignItems: "flex-end" }}>
        <label>Base de datos
          <select value={motor} onChange={(e) => setMotor(e.target.value)}>
            <option value="mysql">MySQL (principal)</option>
            <option value="postgres">PostgreSQL (extra)</option>
          </select>
        </label>
        <button className="btn" onClick={crear} disabled={ocupado}>
          {ocupado ? "Trabajando…" : "💾 Crear respaldo ahora"}
        </button>
      </div>
      <p className="mini">
        Regla 3-2-1: descarga una copia (⬇) y guárdala fuera de esta computadora (USB o nube).
        Un respaldo que nunca se probó no es un respaldo verificado.
      </p>
      <div className="scroll">
        <table>
          <thead><tr><th>Archivo</th><th>Motor</th><th>Tamaño</th><th>Fecha</th><th></th></tr></thead>
          <tbody>
            {lista.map((a) => (
              <tr key={a.nombre}>
                <td>{a.nombre}</td><td>{a.motor}</td><td>{a.kb} KB</td><td>{a.fecha}</td>
                <td>
                  <button className="btn small" disabled={ocupado} onClick={() => restaurar(a)}>Restaurar</button>
                  <button className="btn sec small" onClick={() => descargar(`/api/admin/respaldos/${a.nombre}/descargar`, a.nombre).catch((e) => aviso(e.message, false))}>⬇</button>
                  <button className="btn danger small" onClick={() => eliminar(a)}>✕</button>
                </td>
              </tr>
            ))}
            {lista.length === 0 && <tr><td colSpan="5">Aún no hay respaldos.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}
