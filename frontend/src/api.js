// Funciones para hablar con el backend
let clave = sessionStorage.getItem("claveAdmin") || "";
export const getClave = () => clave;
export function setClave(k) {
  clave = k;
  if (k) sessionStorage.setItem("claveAdmin", k);
  else sessionStorage.removeItem("claveAdmin");
}

export async function api(url, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (url.startsWith("/api/admin") && clave) headers["X-Admin-Key"] = clave; // clave del panel
  const r = await fetch(url, { ...opts, headers });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) {
    const det = d.detail;
    throw new Error(typeof det === "string" ? det
      : Array.isArray(det) ? det.map((x) => x.msg).join("; ") : "Datos inválidos: revisa el formulario");
  }
  return d;
}

export const post = (url, body) =>
  api(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
export const del = (url) => api(url, { method: "DELETE" });

export async function descargar(url, nombre) {
  const r = await fetch(url, { headers: { "X-Admin-Key": clave } });
  if (!r.ok) throw new Error("No se pudo descargar el archivo");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(await r.blob());
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(a.href);
}

export const money = (n) => Number(n).toFixed(2);
