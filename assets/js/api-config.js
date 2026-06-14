// Cambia esta URL cuando tengas el backend desplegado en Render/Replit.
// Ejemplo Render: https://mundial-2026-ai-api.onrender.com
window.MUNDIAL_2026_API_BASE = localStorage.getItem("MUNDIAL_2026_API_BASE") || "http://127.0.0.1:8000";

window.setMundialApiBase = function(url) {
  const clean = String(url || "").replace(/\/$/, "");
  localStorage.setItem("MUNDIAL_2026_API_BASE", clean);
  window.MUNDIAL_2026_API_BASE = clean;
};
