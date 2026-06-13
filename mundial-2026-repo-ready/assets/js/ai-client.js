class MundialAiClient {
  constructor(baseUrl) {
    this.baseUrl = (baseUrl || window.MUNDIAL_API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");
  }

  async request(path, options = {}) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`API ${response.status}: ${text}`);
    }
    return response.json();
  }

  health() {
    return this.request("/api/health");
  }

  clasificacion() {
    return this.request("/api/clasificacion");
  }

  goleadores() {
    return this.request("/api/goleadores");
  }

  partidos() {
    return this.request("/api/partidos");
  }

  qa(question, useLocalModel = false) {
    return this.request("/api/qa", {
      method: "POST",
      body: JSON.stringify({ question, use_local_model: useLocalModel }),
    });
  }
}

window.MundialAiClient = MundialAiClient;
