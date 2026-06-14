window.MUNDIAL_2026_API_BASE = "https://mundial-2026-api-8dvp.onrender.com";

window.addEventListener("load", function () {
  var oldAnswer = window.answerQuestion;
  var base = String(window.MUNDIAL_2026_API_BASE || "").replace(/\/$/, "");
  var words = ["jugador", "jugadores", "joven", "edad", "amarilla", "roja", "expulsado", "minuto", "falta", "portero", "parada", "fuera de juego", "offside", "sustituido", "mejor jugador", "mvp", "penalti"];
  function norm(value) {
    return String(value || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function clean(value) {
    return typeof window.fixText === "function" ? window.fixText(value) : String(value || "");
  }
  async function backend(question) {
    var res = await fetch(base + "/api/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question })
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    var data = await res.json();
    return data.answer || data.response || data.message || "";
  }
  window.answerQuestion = async function (question) {
    var q = norm(question);
    var advanced = words.some(function (w) { return q.indexOf(norm(w)) >= 0; });
    if (advanced) {
      try {
        var answer = await backend(question);
        if (answer) return clean(answer);
      } catch (e) {
        console.warn("QA avanzado no disponible", e);
      }
    }
    if (typeof oldAnswer === "function") return oldAnswer(question);
    try {
      var fallback = await backend(question);
      if (fallback) return clean(fallback);
    } catch (e) {}
    return "Puedo ayudarte con clasificación, resultados, próximos partidos, goleadores y estadísticas avanzadas.";
  };
});
