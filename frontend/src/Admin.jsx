import { useEffect, useState } from "react";
import { api, getClave, setClave } from "./api";
import Respaldos from "./Respaldos.jsx";
import Conexiones from "./Conexiones.jsx";
import Usuarios from "./Usuarios.jsx";

const Si = ({ ok }) => <span className={ok ? "okt" : "bajo"}>{ok ? "✔" : "✖"}</span>;

export default function Admin({ aviso }) {
  const [entrada, setEntrada] = useState("");
  const [estado, setEstado] = useState(null);
  const [sub, setSub] = useState("respaldos");

  async function entrar(k) {
    setClave(k);
    try {
      setEstado(await api("/api/admin/estado"));
    } catch (e) {
      setClave("");
      setEstado(null);
      aviso(e.message, false);
    }
  }

  useEffect(() => { if (getClave()) entrar(getClave()); }, []);

  if (!estado) {
    return (
      <div className="card" style={{ maxWidth: 420 }}>
        <h3>Zona de administración</h3>
        <p className="mini">Escribe la clave <b>ADMIN_KEY</b> de tu archivo .env.</p>
        <div className="row">
          <input type="password" placeholder="Clave de administrador" value={entrada}
                 onChange={(e) => setEntrada(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && entrar(entrada)} />
          <button className="btn" onClick={() => entrar(entrada)}>Entrar</button>
        </div>
      </div>
    );
  }

  const h = estado.herramientas;
  return (
    <>
      <div className="diag">
        <div><Si ok={estado.mysql.ok} /> MySQL admin: {estado.mysql.detalle}</div>
        <div><Si ok={estado.postgres.ok} /> PostgreSQL: {estado.postgres.detalle}</div>
        {Object.keys(h).map((n) => <div key={n}><Si ok={!!h[n]} /> {n}</div>)}
        <div className="mini">Respaldos en: {estado.carpeta_respaldos}</div>
        <div><button className="btn sec small" onClick={() => { setClave(""); setEstado(null); }}>Cerrar sesión admin</button></div>
      </div>

      <div className="subtabs">
        {[["respaldos", "Respaldo y restauración"], ["bd", "Conexión PostgreSQL"], ["usuarios", "Usuarios y permisos"]]
          .map(([id, n]) => <button key={id} className={sub === id ? "on" : ""} onClick={() => setSub(id)}>{n}</button>)}
      </div>

      {sub === "respaldos" && <Respaldos aviso={aviso} />}
      {sub === "bd" && <Conexiones aviso={aviso} />}
      {sub === "usuarios" && <Usuarios aviso={aviso} />}
    </>
  );
}
