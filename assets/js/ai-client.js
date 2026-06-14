async function mundialApi(path, options = {}) {
  const base = (window.MUNDIAL_2026_API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");
  const response = await fetch(base + path, {
    headers: {"Content-Type": "application/json", ...(options.headers || {})},
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API ${response.status}: ${text}`);
  }
  return response.json();
}

window.MundialAI = {
  clasificacion: (grupo) => mundialApi(`/api/clasificacion${grupo ? `?grupo=${encodeURIComponent(grupo)}` : ""}`),
  goleadores: (limit = 50) => mundialApi(`/api/goleadores?limit=${limit}`),
  partidos: () => mundialApi("/api/partidos"),
  equipos: () => mundialApi("/api/equipos"),
  estadios: () => mundialApi("/api/estadios"),
  qa: (question) => mundialApi("/api/qa", {method: "POST", body: JSON.stringify({question})}),
  prediccion: (team_a, team_b) => mundialApi("/api/prediccion", {method: "POST", body: JSON.stringify({team_a, team_b})}),
  sync: () => mundialApi("/api/sync", {method: "POST"}),
};
