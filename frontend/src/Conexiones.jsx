import { useEffect, useState } from "react";
import { api } from "./api";

export default function Conexiones({ aviso }) {
  const [cmp, setCmp] = useState(null);
  const [tablas, setTablas] = useState([]);
  const [motor, setMotor] = useState("postgres");
  const [tabla, setTabla] = useState("");
  const [datos, setDatos] = useState(null);

  useEffect(() => {
    api("/api/admin/esquema").then((e) => { setTablas(Object.keys(e)); setTabla(Object.keys(e)[0]); })
      .catch((e) => aviso(e.message, false));
  }, []);

  async function comparar() {
    try { setCmp(await api("/api/admin/bd/comparar")); } catch (e) { aviso(e.message, false); }
  }
  async function ver() {
    try { setDatos(await api(`/api/admin/bd/tabla/${motor}/${tabla}`)); } catch (e) { aviso(e.message, false); setDatos(null); }
  }

  return (
    <>
      <div className="card">
        <h3>Comparar MySQL contra PostgreSQL</h3>
        <p className="mini">Cuenta las filas de cada tabla en los dos motores para comprobar la migración.</p>
        <button className="btn" onClick={comparar}>Comparar conteos</button>
        {cmp && (
          <table>
            <thead><tr><th>Tabla</th><th>MySQL</th><th>PostgreSQL</th><th></th></tr></thead>
            <tbody>
              {cmp.map((f) => (
                <tr key={f.tabla}>
                  <td>{f.tabla}</td>
                  <td>{f.mysql ?? <span className="bajo">{f.error_mysql}</span>}</td>
                  <td>{f.postgres ?? <span className="bajo">{f.error_postgres}</span>}</td>
                  <td className={f.coincide ? "okt" : "bajo"}>{f.coincide ? "✔ coincide" : "✖ difiere"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3>Ver datos de una tabla</h3>
        <div className="row" style={{ alignItems: "flex-end" }}>
          <label>Motor
            <select value={motor} onChange={(e) => setMotor(e.target.value)}>
              <option value="postgres">PostgreSQL</option><option value="mysql">MySQL</option>
            </select>
          </label>
          <label>Tabla
            <select value={tabla} onChange={(e) => setTabla(e.target.value)}>
              {tablas.map((t) => <option key={t}>{t}</option>)}
            </select>
          </label>
          <button className="btn" onClick={ver}>Ver primeras 20 filas</button>
        </div>
        {datos && (
          <div className="scroll">
            <table>
              <thead><tr>{datos.columnas.map((c) => <th key={c}>{c}</th>)}</tr></thead>
              <tbody>
                {datos.filas.map((f, i) => <tr key={i}>{f.map((v, j) => <td key={j}>{v === null ? "NULL" : String(v)}</td>)}</tr>)}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
