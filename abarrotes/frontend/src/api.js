// Funciones para hablar con el backend
export async function api(url, opts) {
  const r = await fetch(url, opts);
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof d.detail === "string" ? d.detail : "Datos inválidos: revisa el formulario");
  return d;
}

export const post = (url, body) =>
  api(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const money = (n) => Number(n).toFixed(2);
