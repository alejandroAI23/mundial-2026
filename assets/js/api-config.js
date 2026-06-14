window.MUNDIAL_2026_API_BASE = "https://mundial-2026-api-8dvp.onrender.com";

(function () {
  const TEAM_ES = {
    "Mexico": "México", "South Africa": "Sudáfrica", "South Korea": "Corea del Sur", "Czech Republic": "Chequia", "Czechia": "Chequia",
    "Canada": "Canadá", "Bosnia and Herzegovina": "Bosnia y Herzegovina", "Qatar": "Catar", "Switzerland": "Suiza",
    "Brazil": "Brasil", "Morocco": "Marruecos", "Haiti": "Haití", "Scotland": "Escocia", "United States": "Estados Unidos",
    "Paraguay": "Paraguay", "Australia": "Australia", "Turkey": "Turquía", "Türkiye": "Turquía", "Turkiye": "Turquía",
    "Germany": "Alemania", "Curaçao": "Curazao", "Curacao": "Curazao", "Ivory Coast": "Costa de Marfil", "Ecuador": "Ecuador",
    "Netherlands": "Países Bajos", "Japan": "Japón", "Sweden": "Suecia", "Tunisia": "Túnez", "Belgium": "Bélgica",
    "Egypt": "Egipto", "Iran": "Irán", "New Zealand": "Nueva Zelanda", "Spain": "España", "Cape Verde": "Cabo Verde",
    "Saudi Arabia": "Arabia Saudí", "Uruguay": "Uruguay", "France": "Francia", "Senegal": "Senegal", "Iraq": "Irak",
    "Norway": "Noruega", "Argentina": "Argentina", "Algeria": "Argelia", "Austria": "Austria", "Jordan": "Jordania",
    "Portugal": "Portugal", "DR Congo": "RD Congo", "Democratic Republic of the Congo": "RD Congo", "Uzbekistan": "Uzbekistán",
    "Colombia": "Colombia", "England": "Inglaterra", "Croatia": "Croacia", "Ghana": "Ghana", "Panama": "Panamá"
  };

  const FLAG_CODES = {
    "México": "mx", "Sudáfrica": "za", "Corea del Sur": "kr", "Chequia": "cz", "Canadá": "ca", "Bosnia y Herzegovina": "ba",
    "Catar": "qa", "Suiza": "ch", "Brasil": "br", "Marruecos": "ma", "Haití": "ht", "Escocia": "gb-sct",
    "Estados Unidos": "us", "Paraguay": "py", "Australia": "au", "Turquía": "tr", "Alemania": "de", "Curazao": "cw",
    "Costa de Marfil": "ci", "Ecuador": "ec", "Países Bajos": "nl", "Japón": "jp", "Suecia": "se", "Túnez": "tn",
    "Bélgica": "be", "Egipto": "eg", "Irán": "ir", "Nueva Zelanda": "nz", "España": "es", "Cabo Verde": "cv",
    "Arabia Saudí": "sa", "Uruguay": "uy", "Francia": "fr", "Senegal": "sn", "Irak": "iq", "Noruega": "no",
    "Argentina": "ar", "Argelia": "dz", "Austria": "at", "Jordania": "jo", "Portugal": "pt", "RD Congo": "cd",
    "Uzbekistán": "uz", "Colombia": "co", "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa"
  };

  function clean(value) {
    return String(value ?? "")
      .replaceAll("Ã¡", "á").replaceAll("Ã©", "é").replaceAll("Ã­", "í").replaceAll("Ã³", "ó").replaceAll("Ãº", "ú")
      .replaceAll("Ã±", "ñ").replaceAll("Ã§", "ç").replaceAll("Ä‡", "ć").replaceAll("â", "").trim();
  }

  function team(value) {
    const raw = clean(value);
    return TEAM_ES[raw] || raw;
  }

  function translateText(value) {
    let text = clean(value);
    Object.keys(TEAM_ES).sort((a, b) => b.length - a.length).forEach((name) => {
      text = text.replaceAll(name, TEAM_ES[name]);
    });
    return text;
  }

  function parseSourceDate(value) {
    if (!value) return null;
    const raw = String(value).trim();
    const m = raw.match(/^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{1,2}):(\d{2})/);
    if (m) {
      const mm = Number(m[1]);
      const dd = Number(m[2]);
      const yyyy = Number(m[3]);
      const hh = Number(m[4]);
      const min = Number(m[5]);
      return new Date(Date.UTC(yyyy, mm - 1, dd, hh + 4, min));
    }
    const parsed = new Date(raw);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  function madridDate(value) {
    const date = parseSourceDate(value);
    if (!date) return clean(value || "Fecha pendiente");
    return new Intl.DateTimeFormat("es-ES", {
      timeZone: "Europe/Madrid",
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit"
    }).format(date).replace(",", "") + " h España";
  }

  function flagHtml(value) {
    const label = team(value);
    const code = FLAG_CODES[label];
    return code ? `<img src="https://flagcdn.com/32x24/${code}.png" class="flag-img" alt="${label}" onerror="this.outerHTML='🏳️'">` : "🏳️";
  }

  window.Mundial2026Locale = { team, text: translateText, date: madridDate, parseDate: parseSourceDate, flag: flagHtml };

  function installIndexOverrides() {
    if (window.__MUNDIAL_2026_LOCALE_READY__) return;
    if (typeof window.answerQuestion !== "function" || typeof window.renderMatches !== "function") return;
    window.__MUNDIAL_2026_LOCALE_READY__ = true;

    const oldAnswer = window.answerQuestion;
    const base = String(window.MUNDIAL_2026_API_BASE || "").replace(/\/$/, "");
    const words = ["jugador", "jugadores", "joven", "edad", "amarilla", "roja", "expulsado", "minuto", "falta", "portero", "parada", "fuera de juego", "offside", "sustituido", "mejor jugador", "mvp", "penalti"];
    const norm = (v) => String(v || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

    window.teamHome = (match) => team(match.home_team_name_en || match.home_team_label || match.home_team || "Por definir");
    window.teamAway = (match) => team(match.away_team_name_en || match.away_team_label || match.away_team || "Por definir");
    window.flag = flagHtml;
    window.parseDate = parseSourceDate;
    window.formatDate = madridDate;

    async function backend(question) {
      const res = await fetch(base + "/api/qa", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      return data.answer || data.response || data.message || "";
    }

    window.answerQuestion = async function (question) {
      const q = norm(question);
      const advanced = words.some((w) => q.includes(norm(w)));
      if (advanced) {
        try {
          const answer = await backend(question);
          if (answer) return translateText(answer);
        } catch (e) {
          console.warn("QA avanzado no disponible", e);
        }
      }
      const fallback = await oldAnswer(question);
      return translateText(fallback);
    };

    try { window.renderMatches(); } catch (e) {}
    try { window.renderScorers(); } catch (e) {}
  }

  window.addEventListener("load", installIndexOverrides);
  const timer = window.setInterval(() => {
    installIndexOverrides();
    if (window.__MUNDIAL_2026_LOCALE_READY__) window.clearInterval(timer);
  }, 250);
})();
