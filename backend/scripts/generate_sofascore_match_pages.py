from __future__ import annotations

import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATCHES_CSV = ROOT / "backend" / "data" / "sofascore_matches.csv"
OUT_DIR = ROOT / "tools" / "sofascore-partidos"
CONVERTER = "../sofascore-table-converter.html"

STYLE = """
:root{--bg:#071f2a;--card:#fff;--text:#111827;--muted:#64748b;--line:#dbe3ec;--blue:#0f5fd7;--green:#00a870}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Segoe UI,sans-serif;background:linear-gradient(135deg,#082f49,#064e3b);color:var(--text)}
.page{width:min(1400px,calc(100% - 24px));margin:0 auto;padding:24px 0 60px}.hero{color:#fff;margin-bottom:18px}.hero h1{margin:0 0 8px;font-size:clamp(2rem,5vw,4rem);letter-spacing:-.06em;line-height:.95}.hero p{color:rgba(255,255,255,.86);line-height:1.5}.card{background:rgba(255,255,255,.96);border:1px solid rgba(255,255,255,.34);border-radius:22px;padding:18px;box-shadow:0 24px 70px rgba(0,0,0,.18);margin-bottom:16px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px}.match{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:18px;padding:15px;background:#fff}.match:hover{outline:3px solid rgba(15,95,215,.18)}.match strong{font-size:1.05rem}.pill{display:inline-flex;border-radius:999px;background:#e9f7f1;color:#067647;padding:4px 8px;font-weight:900;font-size:.78rem}.muted{color:var(--muted)}.btn{display:inline-flex;text-decoration:none;background:linear-gradient(135deg,var(--blue),var(--green));color:#fff;border-radius:999px;padding:11px 16px;font-weight:900}.frame{width:100%;height:82vh;border:0;border-radius:22px;background:#fff}.top{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.mini{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.mini div{background:#f8fafc;border:1px solid var(--line);border-radius:12px;padding:8px}.mini span{display:block;color:var(--muted);font-size:.78rem;font-weight:900}.mini strong{display:block;font-size:.92rem}@media(max-width:800px){.mini{grid-template-columns:1fr}.frame{height:86vh}}
"""


def slug(value: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in value.strip()).strip("-")


def read_matches() -> list[dict[str, str]]:
    if not MATCHES_CSV.exists():
        return []
    with MATCHES_CSV.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if str(r.get("es_ejemplo", "")).lower() != "true" and r.get("partido_id")]


def esc(value: str) -> str:
    return html.escape(str(value or ""), quote=True)


def js(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")


def page_for_match(match: dict[str, str]) -> str:
    partido_id = match.get("partido_id", "")
    title = f"{match.get('local','')} vs {match.get('visitante','')}"
    return f"""<!DOCTYPE html>
<html lang=\"es\">
<head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>{esc(partido_id)} · Conversor SofaScore</title><style>{STYLE}</style></head>
<body>
<main class=\"page\">
  <section class=\"hero top\">
    <div><h1>{esc(title)}</h1><p>Ficha del partido para completar estadísticas avanzadas desde SofaScore. El conversor inferior se abre ya precargado.</p></div>
    <a class=\"btn\" href=\"index.html\">← Volver al índice</a>
  </section>
  <section class=\"card\">
    <div class=\"mini\">
      <div><span>partido_id</span><strong>{esc(partido_id)}</strong></div>
      <div><span>match_id</span><strong>{esc(match.get('match_id',''))}</strong></div>
      <div><span>fecha</span><strong>{esc(match.get('fecha',''))}</strong></div>
      <div><span>local</span><strong>{esc(match.get('local',''))}</strong></div>
      <div><span>visitante</span><strong>{esc(match.get('visitante',''))}</strong></div>
    </div>
    <p class=\"muted\">Uso rápido: abre SofaScore del partido, copia cada pestaña de estadísticas del jugador y pégala en el conversor de abajo.</p>
  </section>
  <iframe id=\"converter\" class=\"frame\" src=\"{CONVERTER}\"></iframe>
</main>
<script>
const preset = {{partidoId:'{js(partido_id)}', matchId:'{js(match.get('match_id',''))}', fecha:'{js(match.get('fecha',''))}', local:'{js(match.get('local',''))}', visitante:'{js(match.get('visitante',''))}'}};
const frame = document.getElementById('converter');
frame.addEventListener('load', () => {{
  const d = frame.contentDocument || frame.contentWindow.document;
  Object.entries(preset).forEach(([id,value]) => {{ const el = d.getElementById(id); if(el) el.value = value; }});
}});
</script>
</body></html>"""


def index_page(matches: list[dict[str, str]]) -> str:
    cards = []
    for m in matches:
        filename = f"{slug(m['partido_id'])}.html"
        cards.append(f"""<a class=\"match\" href=\"{esc(filename)}\"><span class=\"pill\">{esc(m.get('estado',''))}</span><br><br><strong>{esc(m.get('local',''))} vs {esc(m.get('visitante',''))}</strong><p class=\"muted\">{esc(m.get('fecha',''))} · match_id {esc(m.get('match_id',''))}</p><p><strong>{esc(m.get('partido_id',''))}</strong></p></a>""")
    cards_html = "\n".join(cards) if cards else "<p>No hay partidos reales en backend/data/sofascore_matches.csv.</p>"
    return f"""<!DOCTYPE html>
<html lang=\"es\">
<head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Partidos SofaScore · Mundial 2026</title><style>{STYLE}</style></head>
<body><main class=\"page\"><section class=\"hero\"><h1>Partidos SofaScore · Mundial 2026</h1><p>Elige un partido finalizado. Cada ficha abre el conversor con los datos del partido ya precargados.</p></section><section class=\"card\"><div class=\"grid\">{cards_html}</div></section></main></body></html>"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    matches = read_matches()
    (OUT_DIR / "index.html").write_text(index_page(matches), encoding="utf-8")
    for match in matches:
        (OUT_DIR / f"{slug(match['partido_id'])}.html").write_text(page_for_match(match), encoding="utf-8")
    print(f"Generadas {len(matches)} fichas en {OUT_DIR}")


if __name__ == "__main__":
    main()
