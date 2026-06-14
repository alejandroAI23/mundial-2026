/* Cliente JS reutilizable para conectar GitHub Pages con FastAPI en Render */
(function () {
  const DEFAULT_BASE = "https://mundial-2026-api-8dvp.onrender.com";
  const baseUrl = (window.MUNDIAL_2026_API_BASE || DEFAULT_BASE).replace(/\/$/, "");

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
    return request("/api/clasificacion");
  }

  async function goleadores() {
    return request("/api/goleadores");
  }

  async function partidos() {
    return request("/api/partidos");
  }

  async function prediccion(payload) {
    return request("/api/prediccion", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  function getAnswerText(payload) {
    if (!payload) return "No he recibido respuesta del backend.";
    if (typeof payload === "string") return payload;
    return payload.answer || payload.respuesta || payload.message || payload.prediction || payload.prediccion || JSON.stringify(payload, null, 2);
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
