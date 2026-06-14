// Cambia esta URL cuando tengas el backend desplegado en Render/Replit.
// Ejemplo Render: https://mundial-2026-ai-api.onrender.com
window.MUNDIAL_2026_API_BASE = "https://mundial-2026-api-8dvp.onrender.com";

window.setMundialApiBase = function(url) {
  const clean = String(url || "").replace(/\/$/, "");
  localStorage.setItem("MUNDIAL_2026_API_BASE", clean);
  window.MUNDIAL_2026_API_BASE = clean;
};
