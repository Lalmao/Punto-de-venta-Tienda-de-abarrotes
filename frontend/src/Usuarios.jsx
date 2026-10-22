import { useEffect, useState } from "react";
import { api, post, del } from "./api";

const PRIV_BASE = ["SELECT", "INSERT", "UPDATE", "DELETE", "LOCK TABLES", "SHOW VIEW", "TRIGGER"];
const PRIV_TABLA = ["SELECT", "INSERT", "UPDATE", "DELETE"];
const VACIO = { base: [], con_grant_option: false, tablas: {}, columnas: {} };
const alternar = (lista = [], v) => (lista.includes(v) ? lista.filter((x) => x !== v) : [...lista, v]);

function EditorPermisos({ permisos, setPermisos, esquema }) {
  const todos = permisos.base.includes("ALL PRIVILEGES");
  const setBase = (v) => setPermisos((p) => ({ ...p, base: alternar(p.base, v) }));
  const setTodos = () => setPermisos((p) => ({ ...p, base: todos ? [] : ["ALL PRIVILEGES"], con_grant_option: false }));
  const setTabla = (t, v) => setPermisos((p) => ({ ...p, tablas: { ...p.tablas, [t]: alternar(p.tablas[t], v) } }));
  const setCol = (t, c) => setPermisos((p) => ({
    ...p, columnas: { ...p.columnas, [t]: { ...p.columnas[t], UPDATE: alternar(p.columnas[t]?.UPDATE, c) } },
  }));

  return (
    <>
      <h4>Nivel 1: toda la base de datos</h4>
      <div className="cols">
        <label><input type="checkbox" checked={todos} onChange={setTodos} /> TODOS (administrador)</label>
        {todos && (
          <label><input type="checkbox" checked={permisos.con_grant_option}
            onChange={() => setPermisos((p) => ({ ...p, con_grant_option: !p.con_grant_option }))} /> WITH GRANT OPTION</label>
        )}
        {!todos && PRIV_BASE.map((v) => (
          <label key={v}><input type="checkbox" checked={permisos.base.includes(v)} onChange={() => setBase(v)} /> {v}</label>
        ))}
      </div>

      <h4>Nivel 2 y 3: por tabla y por columna</h4>
      <div className="scroll">
        <table className="perm-grid">
          <thead><tr><th>Tabla</th>{PRIV_TABLA.map((v) => <th key={v}>{v}</th>)}<th>UPDATE solo en columnas</th></tr></thead>
          <tbody>
            {Object.keys(esquema).map((t) => (
              <tr key={t}>
                <td>{t}</td>
                {PRIV_TABLA.map((v) => (
                  <td key={v}><input type="checkbox" checked={(permisos.tablas[t] || []).includes(v)} onChange={() => setTabla(t, v)} /></td>
                ))}
                <td>
                  <details>
                    <summary>{(permisos.columnas[t]?.UPDATE || []).length || "ninguna"}</summary>
                    <div className="cols">
                      {esquema[t].map((c) => (
                        <label key={c}><input type="checkbox" checked={(permisos.columnas[t]?.UPDATE || []).includes(c)} onChange={() => setCol(t, c)} /> {c}</label>
                      ))}
                    </div>
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default function Usuarios({ aviso }) {
  const [lista, setLista] = useState([]);
  const [plantillas, setPlantillas] = useState([]);
  const [esquema, setEsquema] = useState({});
  const [form, setForm] = useState({ usuario: "", host: "localhost", password: "" });
  const [permisos, setPermisos] = useState(VACIO);
  const [editando, setEditando] = useState(null);
  const [grants, setGrants] = useState(null);

  async function cargar() {
    try {
      const [l, p, e] = await Promise.all([api("/api/admin/usuarios"), api("/api/admin/usuarios/plantillas"), api("/api/admin/esquema")]);
      setLista(l); setPlantillas(p); setEsquema(e);
    } catch (e) { aviso(e.message, false); }
  }
  useEffect(() => { cargar(); }, []);

  function elegirPlantilla(id) {
    const p = plantillas.find((x) => x.id === id);
    if (!p) { setPermisos(VACIO); return; }
    setPermisos(structuredClone(p.permisos));
    if (!editando && !form.usuario) setForm((f) => ({ ...f, usuario: p.usuario_sugerido }));
  }

  const qs = (u) => new URLSearchParams({ usuario: u.usuario, host: u.host }).toString();
  const ok = async (fn, texto) => { try { await fn(); aviso(texto); await cargar(); return true; } catch (e) { aviso(e.message, false); return false; } };

  async function guardar() {
    if (editando) {
      const hecho = await ok(() => post("/api/admin/usuarios/permisos", { ...editando, permisos }), `Permisos de ${editando.usuario} actualizados`);
      if (hecho) { setEditando(null); setPermisos(VACIO); }
    } else {
      const hecho = await ok(() => post("/api/admin/usuarios", { ...form, usuario: form.usuario.trim(), host: form.host.trim() || "localhost", permisos }), `Usuario ${form.usuario} creado`);
      if (hecho) { setForm({ usuario: "", host: "localhost", password: "" }); setPermisos(VACIO); }
    }
  }

  async function verGrants(u) {
    try { setGrants({ u, filas: await api("/api/admin/usuarios/grants?" + qs(u)) }); } catch (e) { aviso(e.message, false); }
  }
  function cambiarPassword(u) {
    const pw = window.prompt(`Nueva contraseña para ${u.usuario} (mínimo 8 caracteres):`);
    if (pw) ok(() => post("/api/admin/usuarios/password", { usuario: u.usuario, host: u.host, password: pw }), "Contraseña actualizada");
  }
  function eliminar(u) {
    if (window.confirm(`¿Eliminar a ${u.usuario}@${u.host}? Mejor bloquéalo primero si no estás seguro.`))
      ok(() => del("/api/admin/usuarios?" + qs(u)), "Usuario eliminado");
  }

  return (
    <>
      <div className="card">
        <h3>{editando ? `Cambiar permisos de ${editando.usuario}@${editando.host}` : "Agregar usuario"}</h3>
        <div className="row">
          <label>Plantilla de rol
            <select defaultValue="" onChange={(e) => elegirPlantilla(e.target.value)}>
              <option value="">— personalizado —</option>
              {plantillas.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
            </select>
          </label>
          {!editando && (
            <>
              <label>Usuario <input value={form.usuario} onChange={(e) => setForm({ ...form, usuario: e.target.value })} /></label>
              <label>Host <input value={form.host} onChange={(e) => setForm({ ...form, host: e.target.value })} style={{ width: 110 }} /></label>
              <label>Contraseña (mín. 8) <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
            </>
          )}
        </div>
        <EditorPermisos permisos={permisos} setPermisos={setPermisos} esquema={esquema} />
        <p className="mini">Principio de mínimo privilegio: marca solo lo estrictamente necesario. Los triggers corren con los permisos de quien los creó, así que un cajero no necesita UPDATE sobre PRODUCTO.</p>
        <button className="btn" onClick={guardar}>{editando ? "Reemplazar permisos" : "Crear usuario"}</button>{" "}
        {editando && <button className="btn sec" onClick={() => { setEditando(null); setPermisos(VACIO); }}>Cancelar</button>}
      </div>

      <h3>Usuarios existentes</h3>
      <div className="scroll">
        <table>
          <thead><tr><th>Usuario</th><th>Host</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            {lista.map((u) => (
              <tr key={u.usuario + "@" + u.host}>
                <td>{u.usuario}</td><td>{u.host}</td>
                <td>{u.protegido ? "🔒 protegida" : u.bloqueado ? <span className="bajo">bloqueado</span> : "activo"}</td>
                <td>
                  <button className="btn sec small" onClick={() => verGrants(u)}>Ver permisos</button>
                  {!u.protegido && (
                    <>
                      <button className="btn sec small" onClick={() => { setEditando(u); setPermisos(VACIO); window.scrollTo(0, 0); }}>Editar permisos</button>
                      <button className="btn sec small" onClick={() => cambiarPassword(u)}>Contraseña</button>
                      <button className="btn sec small" onClick={() => ok(() => post("/api/admin/usuarios/bloqueo", { usuario: u.usuario, host: u.host, bloquear: !u.bloqueado }), u.bloqueado ? "Desbloqueado" : "Bloqueado")}>{u.bloqueado ? "Desbloquear" : "Bloquear"}</button>
                      <button className="btn danger small" onClick={() => eliminar(u)}>Eliminar</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {grants && (
        <div className="card">
          <b>SHOW GRANTS de {grants.u.usuario}@{grants.u.host}</b>
          <pre>{grants.filas.join("\n")}</pre>
          <button className="btn sec small" onClick={() => setGrants(null)}>Cerrar</button>
        </div>
      )}
    </>
  );
}
