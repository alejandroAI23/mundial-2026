// Configuración de API para GitHub Pages.
// En local usa http://127.0.0.1:8000.
// En producción cambia DEFAULT_API_BASE por tu URL de Replit/Render.
(function () {
  const DEFAULT_API_BASE = "http://127.0.0.1:8000";
  const params = new URLSearchParams(window.location.search);
  const queryApi = params.get("api");
  if (queryApi) {
    localStorage.setItem("MUNDIAL_API_BASE", queryApi.replace(/\/$/, ""));
  }
  window.MUNDIAL_API_BASE = (localStorage.getItem("MUNDIAL_API_BASE") || DEFAULT_API_BASE).replace(/\/$/, "");
})();
