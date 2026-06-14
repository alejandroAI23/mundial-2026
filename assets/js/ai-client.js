/* Cliente JS reutilizable para conectar GitHub Pages con FastAPI en Render */
(function () {
  const DEFAULT_BASE = "https://mundial-2026-api-8dvp.onrender.com";
  const baseUrl = (window.MUNDIAL_2026_API_BASE || DEFAULT_BASE).replace(/\/$/, "");

  function locale() {
    return window.Mundial2026Locale || null;
  }

  function localizeTeam(value) {
    return locale()?.team ? locale().team(value) : String(value ?? "");
  }

  function localizeText(value) {
    return locale()?.text ? locale().text(value) : String(value ?? "");
  }

  function localizeDate(value) {
    return locale()?.date ? locale().date(value) : String(value ?? "Fecha pendiente");
  }

  async function request(path, options = {}) {
    const response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const message = typeof data === "string" ? data : (data.detail || data.message || JSON.stringify(data));
      throw new Error(`HTTP ${response.status}: ${message}`);
    }
    return data;
  }

  async function health() {
    return request("/health");
  }

  async function qa(question) {
    return request("/api/qa", {
      method: "POST",
      body: JSON.stringify({ question })
    });
  }

  async function clasificacion() {
    const rows = await request("/api/clasificacion");
    return Array.isArray(rows) ? rows.map(row => ({ ...row, team: localizeTeam(row.team) })) : rows;
  }

  async function goleadores() {
    const rows = await request("/api/goleadores");
    return Array.isArray(rows) ? rows.map(row => ({ ...row, team: localizeTeam(row.team) })) : rows;
  }

  async function partidos() {
    const rows = await request("/api/partidos");
    return Array.isArray(rows) ? rows.map(row => ({
      ...row,
      home_team_name_en: localizeTeam(row.home_team_name_en || row.home_team_label || row.home_team),
      away_team_name_en: localizeTeam(row.away_team_name_en || row.away_team_label || row.away_team),
      home_team_label: localizeTeam(row.home_team_label || row.home_team_name_en || row.home_team),
      away_team_label: localizeTeam(row.away_team_label || row.away_team_name_en || row.away_team),
      local_date: localizeDate(row.local_date)
    })) : rows;
  }

  async function prediccion(payload) {
    return request("/api/prediccion", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  function getAnswerText(payload) {
    if (!payload) return "No he recibido respuesta del backend.";
    if (typeof payload === "string") return localizeText(payload);
    const text = payload.answer || payload.respuesta || payload.message || payload.prediction || payload.prediccion || JSON.stringify(payload, null, 2);
    return localizeText(text);
  }

  window.Mundial2026Api = {
    baseUrl,
    request,
    health,
    qa,
    clasificacion,
    goleadores,
    partidos,
    prediccion,
    getAnswerText
  };
})();
