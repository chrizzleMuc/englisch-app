// Mathe-Bilder für die 1. Klasse, als SVG direkt im Programm gezeichnet (keine Dateien nötig).
// Eine Aufgabe nennt das Bild mit einem kurzen Code im Feld "vis", z. B.:
//   feld:7        Zehnerfeld mit 7 Punkten          feld:5+3   zwei Farben
//   zf:13         Zwanzigerfeld                     zf:8+5     zwei Farben (Zehnerübergang)
//   uhr:3         Uhr, 3 Uhr                        uhr:3:30   halb vier
//   geld:2,1,0.5  Münzen und Scheine in Euro
//   form:kreis    eine Form (kreis, dreieck, quadrat, rechteck)
//   formen:kreis,dreieck,kreis   mehrere Formen nebeneinander
//   mauer:?;3,4   Zahlenmauer, Reihen von oben nach unten, ? = gesuchte Zahl
//   strich:7      Strichliste
//   lage:🐱:links:📦   Katze links von der Kiste (links, rechts, oben, unten, vor, in)
//   sym:herz      Figur mit Spiegelachse
//   balken:🍎=4,🍌=2   Säulendiagramm
//   zug:3,4,?,6   Zahlenzug (Waggons)
//   haus:7;3,?    Zahlenhaus: Dach 7, Stockwerk 3 und ?
//   menge:🍎*5+🍎*3   Dinge zum Zählen, in Fünferreihen (mit + zwischen zwei Gruppen)
// 3. Klasse:
//   st:352        Stellentafel H Z E mit Ziffern (? = Lücke)    stp:352  Stellentafel mit Plättchen
//   hze:352       Hunderterplatten, Zehnerstangen, Einerwürfel
//   strahl:300:400:350   Zahlenstrahl von 300 bis 400, Pfeil mit ? bei 350 (optional :Teilstrich-Abstand)
//   kreuz:5:10,3  Malkreuz 5 · (10 + 3)
//   koerper:wuerfel  Körper (wuerfel, quader, kugel, zylinder, kegel, pyramide)
//   netz:1,0;0,1;1,1;2,1;3,1;1,2   Körpernetz aus Quadraten (Spalte,Zeile)
//   bau:2,1;1,1   Würfelgebäude, Höhen je Feld, Reihen von hinten nach vorn
//   linien:parallel   zwei Linien (parallel, parallel2, senkrecht, schief)
//   flaeche:4x3   Fläche aus Kästchen (oder einzelne Kästchen 0,0;1,0;...)
//   tafel:340:362 Ausschnitt der Tausendertafel ab 340 (5 Spalten, 3 Reihen), ? bei 362
import { pic } from "./pics.js";

const C = { red: "#e5484d", blue: "#3b6fd8", empty: "#ffffff", line: "#5b3fa6", ink: "#2a1a4f", soft: "#f6f0ff", gold: "#f2b733", silver: "#c9ccd6", copper: "#c77b45" };
const svg = (w, h, body, cls = "") => `<svg class="vis ${cls}" viewBox="0 0 ${w} ${h}" role="img" xmlns="http://www.w3.org/2000/svg">${body}</svg>`;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

function counts(s) {
  const [a, b] = s.split("+").map(Number);
  return [a || 0, b || 0];
}

// Zehnerfeld (2 x 5) oder Zwanzigerfeld (2 x 10, Lücke nach 5)
function field(arg, cols) {
  const [a, b] = counts(arg);
  const r = 15;
  const gap = 38;
  const mid = cols === 10 ? 14 : 0;
  const w = cols * gap + mid + 16;
  const h = 2 * gap + 16;
  let out = `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="12" fill="${C.soft}" stroke="${C.line}" stroke-width="3"/>`;
  out += `<line x1="8" y1="${h / 2}" x2="${w - 8}" y2="${h / 2}" stroke="${C.line}" stroke-opacity=".25" stroke-width="2"/>`;
  if (cols === 10) out += `<line x1="${w / 2}" y1="8" x2="${w / 2}" y2="${h - 8}" stroke="${C.line}" stroke-opacity=".25" stroke-width="2"/>`;
  for (let i = 0; i < cols * 2; i++) {
    const row = Math.floor(i / cols);
    const col = i % cols;
    const x = 8 + gap / 2 + col * gap + (col >= 5 ? mid : 0);
    const y = 8 + gap / 2 + row * gap;
    const fill = i < a ? C.red : i < a + b ? C.blue : C.empty;
    out += `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${fill === C.empty ? "#b9a8e0" : "rgba(0,0,0,.15)"}" stroke-width="2"/>`;
  }
  return svg(w, h, out, "vis-field");
}

function clock(arg) {
  const [h, m = 0] = arg.split(":").map(Number);
  const R = 90;
  const c = 100;
  let out = `<circle cx="${c}" cy="${c}" r="${R}" fill="#fff" stroke="${C.line}" stroke-width="8"/>`;
  for (let i = 1; i <= 12; i++) {
    const a = (i / 12) * 2 * Math.PI;
    out += `<text x="${c + Math.sin(a) * 60}" y="${c - Math.cos(a) * 60 + 8}" text-anchor="middle" font-size="22" font-weight="800" fill="${C.ink}" font-family="system-ui,sans-serif">${i}</text>`;
  }
  for (let i = 0; i < 60; i++) {
    const a = (i / 60) * 2 * Math.PI;
    const r1 = i % 5 ? 82 : 78;
    out += `<line x1="${c + Math.sin(a) * r1}" y1="${c - Math.cos(a) * r1}" x2="${c + Math.sin(a) * 86}" y2="${c - Math.cos(a) * 86}" stroke="${C.ink}" stroke-width="${i % 5 ? 1.5 : 3}"/>`;
  }
  const ha = (((h % 12) + m / 60) / 12) * 2 * Math.PI;
  const ma = (m / 60) * 2 * Math.PI;
  out += `<line x1="${c}" y1="${c}" x2="${c + Math.sin(ma) * 70}" y2="${c - Math.cos(ma) * 70}" stroke="${C.blue}" stroke-width="7" stroke-linecap="round"/>`;
  out += `<line x1="${c}" y1="${c}" x2="${c + Math.sin(ha) * 46}" y2="${c - Math.cos(ha) * 46}" stroke="${C.red}" stroke-width="10" stroke-linecap="round"/>`;
  out += `<circle cx="${c}" cy="${c}" r="8" fill="${C.ink}"/>`;
  return svg(200, 200, out, "vis-clock");
}

// Münzen und Scheine (eigene, vereinfachte Zeichnung, keine echten Motive)
function money(arg) {
  const vals = arg.split(",").map(Number).filter((v) => v > 0);
  let x = 6;
  let out = "";
  const H = 110;
  for (const v of vals) {
    if (v >= 5) {
      const col = v === 5 ? "#9aa3ad" : v === 10 ? "#e07a6b" : v === 20 ? "#6f9be0" : "#e0a34a";
      out += `<rect x="${x}" y="15" width="150" height="80" rx="8" fill="${col}" stroke="rgba(0,0,0,.25)" stroke-width="2"/><rect x="${x + 8}" y="23" width="134" height="64" rx="5" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/><text x="${x + 75}" y="68" text-anchor="middle" font-size="34" font-weight="900" fill="#fff" font-family="system-ui,sans-serif">${v} €</text>`;
      x += 160;
      continue;
    }
    const euro = v >= 1;
    const r = { 0.01: 24, 0.02: 27, 0.05: 30, 0.1: 29, 0.2: 32, 0.5: 35, 1: 34, 2: 38 }[v] || 30;
    const cx = x + r;
    const cy = H / 2;
    const label = euro ? `${v} €` : `${Math.round(v * 100)} ct`;
    if (v === 1) out += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${C.gold}"/><circle cx="${cx}" cy="${cy}" r="${r * 0.7}" fill="${C.silver}"/>`;
    else if (v === 2) out += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${C.silver}"/><circle cx="${cx}" cy="${cy}" r="${r * 0.7}" fill="${C.gold}"/>`;
    else out += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${v < 0.1 ? C.copper : C.gold}"/>`;
    out += `<circle cx="${cx}" cy="${cy}" r="${r - 1}" fill="none" stroke="rgba(0,0,0,.25)" stroke-width="2"/>`;
    out += `<text x="${cx}" y="${cy + (euro ? 9 : 6)}" text-anchor="middle" font-size="${euro ? 24 : 16}" font-weight="900" fill="${C.ink}" font-family="system-ui,sans-serif">${label}</text>`;
    x += 2 * r + 10;
  }
  return svg(Math.max(x, 60), H, out, "vis-money");
}

const SHAPE_COL = { kreis: "#e5484d", dreieck: "#2a9d8f", quadrat: "#3b6fd8", rechteck: "#f2b733" };
function shape(name, x = 0, size = 100) {
  const s = size;
  const col = SHAPE_COL[name] || "#7b3fe4";
  const st = `fill="${col}" stroke="rgba(0,0,0,.2)" stroke-width="3"`;
  if (name === "kreis") return `<circle cx="${x + s / 2}" cy="${s / 2}" r="${s * 0.42}" ${st}/>`;
  if (name === "dreieck") return `<polygon points="${x + s / 2},${s * 0.08} ${x + s * 0.94},${s * 0.9} ${x + s * 0.06},${s * 0.9}" ${st}/>`;
  if (name === "quadrat") return `<rect x="${x + s * 0.1}" y="${s * 0.1}" width="${s * 0.8}" height="${s * 0.8}" ${st}/>`;
  if (name === "rechteck") return `<rect x="${x + s * 0.02}" y="${s * 0.26}" width="${s * 0.96}" height="${s * 0.5}" ${st}/>`;
  return "";
}
function shapes(arg) {
  const list = arg.split(",");
  return svg(list.length * 110, 100, list.map((n, i) => shape(n, i * 110)).join(""), "vis-shapes");
}

// Zahlenmauer: Reihen von oben nach unten, z. B. "?;3,4" oder "?;?,5;2,3,2"
function wall(arg) {
  const rows = arg.split(";").map((r) => r.split(","));
  const n = rows.length;
  const bw = 80;
  const bh = 54;
  const w = rows[n - 1].length * bw + 8;
  let out = "";
  rows.forEach((row, ri) => {
    const off = (w - row.length * bw) / 2;
    row.forEach((v, i) => {
      const x = off + i * bw;
      const y = 4 + ri * bh;
      const q = v === "?";
      out += `<rect x="${x + 2}" y="${y}" width="${bw - 4}" height="${bh - 4}" rx="6" fill="${q ? "#ffe9a8" : "#fff"}" stroke="${C.line}" stroke-width="3"/>`;
      out += `<text x="${x + bw / 2}" y="${y + 36}" text-anchor="middle" font-size="28" font-weight="900" fill="${q ? "#b07a00" : C.ink}" font-family="system-ui,sans-serif">${esc(v)}</text>`;
    });
  });
  return svg(w, n * bh + 8, out, "vis-wall");
}

// Zahlenhaus: Dach = Zahl, darunter ein Stockwerk mit zwei Zahlen
function house(arg) {
  const [roof, floor] = arg.split(";");
  const [a, b] = floor.split(",");
  const cell = (x, v) => {
    const q = v === "?";
    return `<rect x="${x}" y="80" width="80" height="56" fill="${q ? "#ffe9a8" : "#fff"}" stroke="${C.line}" stroke-width="3"/><text x="${x + 40}" y="118" text-anchor="middle" font-size="30" font-weight="900" fill="${q ? "#b07a00" : C.ink}" font-family="system-ui,sans-serif">${esc(v)}</text>`;
  };
  const out = `<polygon points="10,80 90,8 170,80" fill="#e5484d" stroke="${C.line}" stroke-width="3"/><text x="90" y="66" text-anchor="middle" font-size="32" font-weight="900" fill="#fff" font-family="system-ui,sans-serif">${esc(roof)}</text>${cell(10, a)}${cell(90, b)}`;
  return svg(180, 140, out, "vis-house");
}

function tally(arg) {
  const n = Number(arg);
  let out = "";
  let x = 10;
  for (let g = 0; g < Math.ceil(n / 5); g++) {
    const k = Math.min(5, n - g * 5);
    for (let i = 0; i < Math.min(k, 4); i++) out += `<line x1="${x + i * 16}" y1="10" x2="${x + i * 16}" y2="80" stroke="${C.ink}" stroke-width="6" stroke-linecap="round"/>`;
    if (k === 5) out += `<line x1="${x - 8}" y1="70" x2="${x + 56}" y2="20" stroke="${C.red}" stroke-width="6" stroke-linecap="round"/>`;
    x += 90;
  }
  return svg(Math.max(x, 60), 90, out, "vis-tally");
}

function emo(ch, x, y, s) {
  const html = pic(ch);
  const src = /src="([^"]+)"/.exec(html);
  return src ? `<image href="${src[1]}" x="${x}" y="${y}" width="${s}" height="${s}"/>` : `<text x="${x + s / 2}" y="${y + s * 0.85}" font-size="${s * 0.85}" text-anchor="middle">${esc(ch)}</text>`;
}

// Dinge zum Zählen: Gruppen "🍎*5", getrennt durch "+", je Gruppe Reihen zu 5
function amount(arg) {
  const groups = arg.split("+").map((g) => {
    const [e, n] = g.split("*");
    return [e, Number(n) || 1];
  });
  const s = 56;
  let x = 0;
  let out = "";
  let H = 0;
  groups.forEach(([e, n], gi) => {
    if (gi) {
      out += `<text x="${x + 22}" y="__MID__" font-size="48" font-weight="900" text-anchor="middle" fill="${C.ink}" font-family="system-ui,sans-serif">+</text>`;
      x += 44;
    }
    const cols = Math.min(5, n);
    for (let i = 0; i < n; i++) out += emo(e, x + (i % 5) * s, Math.floor(i / 5) * s, s - 4);
    H = Math.max(H, Math.ceil(n / 5) * s);
    x += cols * s + 8;
  });
  return svg(x, H, out.replaceAll("__MID__", String(H / 2 + 16)), "vis-amount");
}

// Muster: alle Bilder in einer Reihe (Zeichen, ? = Lücke)
function row(arg) {
  const items = [...(typeof Intl !== "undefined" && Intl.Segmenter ? [...new Intl.Segmenter("de", { granularity: "grapheme" }).segment(arg)].map((x) => x.segment) : [...arg])];
  const s = 60;
  const out = items.map((e, i) => (e === "?" ? `<rect x="${i * s + 4}" y="4" width="${s - 8}" height="${s - 8}" rx="10" fill="#ffe9a8" stroke="${C.line}" stroke-width="3" stroke-dasharray="6 5"/><text x="${i * s + s / 2}" y="${s / 2 + 12}" font-size="34" font-weight="900" text-anchor="middle" fill="#b07a00" font-family="system-ui,sans-serif">?</text>` : emo(e, i * s + 2, 2, s - 4))).join("");
  return svg(items.length * s, s, out, "vis-row");
}

// Lage: Tier links/rechts/oben/unten/vor/in von einem Gegenstand
function place(arg) {
  const [a, where, b] = arg.split(":");
  const box = emo(b, 92, 88, 100);
  const pos = { links: [0, 98], rechts: [196, 98], oben: [100, 0], unten: [100, 190], vor: [112, 120], in: [112, 92] }[where] || [0, 98];
  const animal = emo(a, pos[0], pos[1], where === "in" ? 56 : 86);
  return svg(284, 278, where === "vor" ? box + animal : animal + box, "vis-place");
}

const SYM = {
  herz: "M100 170 C20 110 10 60 50 40 C75 28 95 45 100 60 C105 45 125 28 150 40 C190 60 180 110 100 170 Z",
  haus: "M40 170 L40 85 L100 30 L160 85 L160 170 Z",
  stern: "M100 20 L120 75 L178 75 L131 108 L149 165 L100 130 L51 165 L69 108 L22 75 L80 75 Z",
  blatt: "M100 20 C160 60 160 140 100 180 C40 140 40 60 100 20 Z",
  schief: "M40 170 L60 40 L150 70 L170 170 Z",
  welle: "M30 150 C40 60 90 40 110 90 C125 130 160 120 170 40 L170 170 L30 170 Z",
  fahne: "M50 180 L50 20 L160 50 L60 85 Z",
  stiefel: "M60 20 L110 20 L110 120 L170 130 L170 175 L60 175 Z",
};
function symmetry(arg) {
  const d = SYM[arg] || SYM.herz;
  return svg(200, 200, `<path d="${d}" fill="#a77bff" stroke="${C.line}" stroke-width="4" stroke-linejoin="round"/><line x1="100" y1="6" x2="100" y2="194" stroke="${C.red}" stroke-width="4" stroke-dasharray="10 8"/>`, "vis-sym");
}

function bars(arg) {
  const items = arg.split(",").map((p) => p.split("="));
  const max = Math.max(...items.map((p) => Number(p[1])));
  const bw = 70;
  const unit = 22;
  const H = max * unit + 90;
  let out = "";
  for (let v = 1; v <= max; v++) out += `<line x1="30" y1="${H - 60 - v * unit}" x2="${items.length * bw + 30}" y2="${H - 60 - v * unit}" stroke="#d9ccf5" stroke-width="1.5"/><text x="20" y="${H - 54 - v * unit}" font-size="14" text-anchor="end" fill="${C.ink}" font-family="system-ui,sans-serif">${v}</text>`;
  items.forEach(([e, n], i) => {
    const x = 40 + i * bw;
    out += `<rect x="${x}" y="${H - 60 - n * unit}" width="${bw - 20}" height="${n * unit}" rx="4" fill="${[C.red, C.blue, "#2a9d8f", C.gold][i % 4]}"/>`;
    out += emo(e, x + 1, H - 54, 48);
  });
  out += `<line x1="30" y1="${H - 60}" x2="${items.length * bw + 30}" y2="${H - 60}" stroke="${C.ink}" stroke-width="3"/>`;
  return svg(items.length * bw + 40, H, out, "vis-bars");
}

function train(arg) {
  const vals = arg.split(",");
  const cw = 74;
  let out = `<rect x="4" y="22" width="62" height="56" rx="8" fill="${C.red}"/><rect x="40" y="6" width="22" height="20" fill="${C.ink}"/><circle cx="20" cy="84" r="9" fill="${C.ink}"/><circle cx="52" cy="84" r="9" fill="${C.ink}"/>`;
  vals.forEach((v, i) => {
    const x = 74 + i * cw;
    const q = v === "?";
    out += `<line x1="${x - 8}" y1="60" x2="${x}" y2="60" stroke="${C.ink}" stroke-width="4"/><rect x="${x}" y="22" width="${cw - 8}" height="56" rx="6" fill="${q ? "#ffe9a8" : "#fff"}" stroke="${C.line}" stroke-width="3"/><text x="${x + (cw - 8) / 2}" y="60" text-anchor="middle" font-size="26" font-weight="900" fill="${q ? "#b07a00" : C.ink}" font-family="system-ui,sans-serif">${esc(v)}</text><circle cx="${x + 14}" cy="84" r="8" fill="${C.ink}"/><circle cx="${x + cw - 22}" cy="84" r="8" fill="${C.ink}"/>`;
  });
  return svg(80 + vals.length * cw, 96, out, "vis-train");
}


// ---------- 3. Klasse ----------
const PLACE = [
  { k: "H", col: "#3b6fd8", bg: "#e3ecff" },
  { k: "Z", col: "#2a9d8f", bg: "#dcf3ef" },
  { k: "E", col: "#e5484d", bg: "#fde4e4" },
];
const FONT = 'font-family="system-ui,sans-serif"';

// Stellentafel: Ziffern oder Plättchen (Punkte)
function placeTable(arg, dots) {
  const d = arg.padStart(3, " ").slice(-3).split("");
  const cw = dots ? 120 : 84;
  const hh = 44;
  const bh = dots ? 92 : 70;
  let out = "";
  d.forEach((v, i) => {
    const p = PLACE[i];
    const x = 4 + i * cw;
    out += `<rect x="${x}" y="4" width="${cw}" height="${hh}" fill="${p.bg}" stroke="${C.line}" stroke-width="3"/><text x="${x + cw / 2}" y="37" text-anchor="middle" font-size="28" font-weight="900" fill="${p.col}" ${FONT}>${p.k}</text>`;
    const q = v === "?";
    out += `<rect x="${x}" y="${4 + hh}" width="${cw}" height="${bh}" fill="${q ? "#ffe9a8" : "#fff"}" stroke="${C.line}" stroke-width="3"/>`;
    if (dots && !q) {
      const n = Number(v) || 0;
      for (let k = 0; k < n; k++) {
        const cx = x + 22 + (k % 4) * 25;
        const cy = 4 + hh + 22 + Math.floor(k / 4) * 25;
        out += `<circle cx="${cx}" cy="${cy}" r="10" fill="${p.col}"/>`;
      }
    } else if (v.trim()) {
      out += `<text x="${x + cw / 2}" y="${4 + hh + bh / 2 + 15}" text-anchor="middle" font-size="44" font-weight="900" fill="${q ? "#b07a00" : C.ink}" ${FONT}>${esc(v)}</text>`;
    }
  });
  return svg(cw * 3 + 8, hh + bh + 8, out, "vis-st");
}

// Hunderterplatten, Zehnerstangen, Einerwürfel
function blocks(arg) {
  const n = Number(arg) || 0;
  const [h, z, e] = [Math.floor(n / 100), Math.floor(n / 10) % 10, n % 10];
  const u = 9;
  let x = 6;
  let out = "";
  const H = 10 * u + 12;
  const cube = (cx, cy, fill) => `<rect x="${cx}" y="${cy}" width="${u}" height="${u}" fill="${fill}" stroke="rgba(0,0,0,.28)" stroke-width="1"/>`;
  for (let i = 0; i < h; i++) {
    for (let r = 0; r < 10; r++) for (let c = 0; c < 10; c++) out += cube(x + c * u, 6 + r * u, PLACE[0].col);
    x += 10 * u + 10;
  }
  for (let i = 0; i < z; i++) {
    for (let r = 0; r < 10; r++) out += cube(x, 6 + r * u, PLACE[1].col);
    x += u + 8;
  }
  if (e) x += 4;
  for (let i = 0; i < e; i++) {
    out += cube(x + (i % 2) * (u + 3), 6 + 10 * u - (Math.floor(i / 2) + 1) * (u + 3), PLACE[2].col);
  }
  if (e) x += 2 * u + 8;
  return svg(Math.max(x, 40), H, out, "vis-hze");
}

// Zahlenstrahl mit Pfeil auf der gesuchten Zahl
function numberLine(arg) {
  const [a, b, q, stepArg] = arg.split(":").map(Number);
  const W = 560;
  const x0 = 24;
  const x1 = W - 24;
  const span = b - a;
  const step = stepArg || (span <= 100 ? 10 : span <= 200 ? 10 : 50);
  const X = (v) => x0 + ((v - a) / span) * (x1 - x0);
  let out = `<line x1="${x0 - 10}" y1="80" x2="${x1 + 14}" y2="80" stroke="${C.ink}" stroke-width="4"/><polygon points="${x1 + 20},80 ${x1 + 8},73 ${x1 + 8},87" fill="${C.ink}"/>`;
  const fine = step / 5 >= 1 && (span / step) * 5 <= 60 ? step / 5 : 0;
  if (fine) for (let v = a; v <= b; v += fine) out += `<line x1="${X(v)}" y1="74" x2="${X(v)}" y2="86" stroke="${C.ink}" stroke-width="1.5"/>`;
  for (let v = a; v <= b; v += step) {
    const big = (v - a) % (step * 5) === 0 || v === b;
    out += `<line x1="${X(v)}" y1="${big ? 64 : 68}" x2="${X(v)}" y2="${big ? 96 : 92}" stroke="${C.ink}" stroke-width="${big ? 3.5 : 2.5}"/>`;
    if (big) out += `<text x="${X(v)}" y="122" text-anchor="middle" font-size="20" font-weight="800" fill="${C.ink}" ${FONT}>${v}</text>`;
  }
  if (!isNaN(q)) {
    const x = X(q);
    out += `<rect x="${x - 28}" y="6" width="56" height="34" rx="9" fill="#ffe9a8" stroke="${C.line}" stroke-width="3"/><text x="${x}" y="32" text-anchor="middle" font-size="24" font-weight="900" fill="#b07a00" ${FONT}>?</text><line x1="${x}" y1="40" x2="${x}" y2="66" stroke="${C.red}" stroke-width="4"/><polygon points="${x},72 ${x - 7},60 ${x + 7},60" fill="${C.red}"/>`;
  }
  return svg(W, 132, out, "vis-line");
}

// Ausschnitt der Tausendertafel: erste Zahl steht da, ? bei der gesuchten
function thousandGrid(arg) {
  const [start, q, colsArg, rowsArg] = arg.split(":").map(Number);
  const cols = colsArg || 5;
  const rows = rowsArg || 3;
  const cw = 84;
  const ch = 54;
  let out = "";
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      const v = start + r * 10 + c;
      const isQ = v === q;
      const shown = r === 0 && c === 0;
      const x = 4 + c * cw;
      const y = 4 + r * ch;
      out += `<rect x="${x}" y="${y}" width="${cw}" height="${ch}" fill="${isQ ? "#ffe9a8" : shown ? "#e3ecff" : "#fff"}" stroke="${C.line}" stroke-width="2.5"/>`;
      if (shown || isQ) out += `<text x="${x + cw / 2}" y="${y + 37}" text-anchor="middle" font-size="26" font-weight="900" fill="${isQ ? "#b07a00" : C.ink}" ${FONT}>${isQ ? "?" : v}</text>`;
    }
  return svg(cols * cw + 8, rows * ch + 8, out, "vis-tafel");
}

// Malkreuz: kreuz:5:10,3  → 5 mal (10 und 3), Ergebnisfelder mit ?
function malkreuz(arg) {
  const [a, parts] = arg.split(":");
  const ps = parts.split(",");
  const cw = 92;
  const ch = 58;
  let out = "";
  const cell = (x, y, v, fill, col) => `<rect x="${x}" y="${y}" width="${cw}" height="${ch}" fill="${fill}" stroke="${C.line}" stroke-width="2.5"/><text x="${x + cw / 2}" y="${y + 40}" text-anchor="middle" font-size="28" font-weight="900" fill="${col}" ${FONT}>${esc(v)}</text>`;
  out += cell(4, 4, "·", "#efe6ff", C.ink);
  ps.forEach((v, i) => (out += cell(4 + (i + 1) * cw, 4, v, "#e3ecff", C.blue)));
  out += cell(4, 4 + ch, a, "#fde4e4", C.red);
  ps.forEach((v, i) => (out += cell(4 + (i + 1) * cw, 4 + ch, "?", "#ffe9a8", "#b07a00")));
  return svg((ps.length + 1) * cw + 8, 2 * ch + 8, out, "vis-kreuz");
}

// Geometrische Körper (vereinfachte 3D-Zeichnung)
function solid(arg) {
  const st = `stroke="${C.line}" stroke-width="3" stroke-linejoin="round"`;
  const hid = `stroke="${C.line}" stroke-width="2" stroke-dasharray="6 5" fill="none"`;
  const A = "#b9a3f5";
  const B = "#9a7ff0";
  const T = "#d9ccfb";
  let o = "";
  switch (arg) {
    case "wuerfel":
      o = `<polygon points="40,70 140,70 140,170 40,170" fill="${A}" ${st}/><polygon points="40,70 80,35 180,35 140,70" fill="${T}" ${st}/><polygon points="140,70 180,35 180,135 140,170" fill="${B}" ${st}/><polyline points="40,170 80,135 180,135" ${hid}/><line x1="80" y1="35" x2="80" y2="135" ${hid}/>`;
      break;
    case "quader":
      o = `<polygon points="20,85 150,85 150,165 20,165" fill="${A}" ${st}/><polygon points="20,85 55,55 185,55 150,85" fill="${T}" ${st}/><polygon points="150,85 185,55 185,135 150,165" fill="${B}" ${st}/><polyline points="20,165 55,135 185,135" ${hid}/><line x1="55" y1="55" x2="55" y2="135" ${hid}/>`;
      break;
    case "kugel":
      o = `<defs><radialGradient id="kg" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="#efe8ff"/><stop offset="1" stop-color="${B}"/></radialGradient></defs><circle cx="100" cy="100" r="72" fill="url(#kg)" ${st}/><ellipse cx="100" cy="100" rx="72" ry="18" fill="none" stroke="${C.line}" stroke-width="1.5" stroke-dasharray="6 5"/>`;
      break;
    case "zylinder":
      o = `<path d="M45 50 L45 155 A55 16 0 0 0 155 155 L155 50" fill="${A}" ${st}/><ellipse cx="100" cy="50" rx="55" ry="16" fill="${T}" ${st}/><path d="M45 155 A55 16 0 0 1 155 155" ${hid}/>`;
      break;
    case "kegel":
      o = `<path d="M100 22 L40 160 A60 17 0 0 0 160 160 Z" fill="${A}" ${st}/><path d="M40 160 A60 17 0 0 1 160 160" ${hid}/>`;
      break;
    case "pyramide":
      o = `<polygon points="100,20 30,160 130,175" fill="${A}" ${st}/><polygon points="100,20 130,175 175,140" fill="${B}" ${st}/><polyline points="30,160 75,128 175,140" ${hid}/><line x1="100" y1="20" x2="75" y2="128" ${hid}/>`;
      break;
  }
  return svg(200, 190, o, "vis-solid");
}

// Netz: Quadrate auf Kästchen, "netz:1,0;0,1;1,1;2,1;3,1;1,2" (Spalte,Zeile)
function net(arg) {
  const cells = arg.split(";").map((c) => c.split(",").map(Number));
  const s = 44;
  const w = Math.max(...cells.map((c) => c[0])) + 1;
  const h = Math.max(...cells.map((c) => c[1])) + 1;
  const out = cells.map(([x, y]) => `<rect x="${4 + x * s}" y="${4 + y * s}" width="${s}" height="${s}" fill="#b9a3f5" stroke="${C.line}" stroke-width="3"/>`).join("");
  return svg(w * s + 8, h * s + 8, out, "vis-net");
}

// Würfelgebäude: "bau:2,1,1;1,0,0" = Höhen je Feld, Reihen von hinten nach vorn
function building(arg) {
  const rows = arg.split(";").map((r) => r.split(",").map(Number));
  const s = 34;
  const dx = s * 0.5;
  const dy = s * 0.5;
  const maxH = Math.max(...rows.flat());
  const cols = Math.max(...rows.map((r) => r.length));
  const W = cols * s + rows.length * dx + 10;
  const H = maxH * s + rows.length * dy + s + 10;
  let out = "";
  const cube = (x, y) =>
    `<polygon points="${x},${y} ${x + s},${y} ${x + s},${y + s} ${x},${y + s}" fill="#3b6fd8" stroke="#1d3f8f" stroke-width="2"/>` +
    `<polygon points="${x},${y} ${x + dx},${y - dy} ${x + s + dx},${y - dy} ${x + s},${y}" fill="#7fa6f0" stroke="#1d3f8f" stroke-width="2"/>` +
    `<polygon points="${x + s},${y} ${x + s + dx},${y - dy} ${x + s + dx},${y + s - dy} ${x + s},${y + s}" fill="#2a56b8" stroke="#1d3f8f" stroke-width="2"/>`;
  rows.forEach((r, ri) => {
    const back = rows.length - 1 - ri;
    r.forEach((hgt, ci) => {
      for (let k = 0; k < hgt; k++) {
        const x = 5 + ci * s + back * dx;
        const y = H - 5 - s - (rows.length - 1 - back) * 0 - back * dy - k * s;
        out += cube(x, y);
      }
    });
  });
  return svg(W, H, out, "vis-bau");
}

// Zwei Linien: parallel, senkrecht oder schief
function lines(arg) {
  const grid = Array.from({ length: 9 }, (_, i) => `<line x1="${10 + i * 25}" y1="10" x2="${10 + i * 25}" y2="190" stroke="#e1d6fa"/><line x1="10" y1="${10 + i * 22.5}" x2="210" y2="${10 + i * 22.5}" stroke="#e1d6fa"/>`).join("");
  const L = { parallel: [[35, 40, 185, 90], [35, 110, 185, 160]], senkrecht: [[30, 100, 190, 100], [110, 25, 110, 175]], schief: [[30, 60, 190, 120], [60, 170, 170, 30]], parallel2: [[60, 20, 110, 180], [120, 20, 170, 180]] }[arg] || [];
  const out = L.map(([a, b, c, d], i) => `<line x1="${a}" y1="${b}" x2="${c}" y2="${d}" stroke="${i ? C.red : C.blue}" stroke-width="6" stroke-linecap="round"/>`).join("");
  return svg(220, 200, grid + out, "vis-lines");
}

// Fläche aus Kästchen: "flaeche:4x3" Rechteck oder "flaeche:0,0;1,0;1,1" einzelne Kästchen
function area(arg) {
  let cells;
  if (/^\d+x\d+$/.test(arg)) {
    const [w, h] = arg.split("x").map(Number);
    cells = [];
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) cells.push([x, y]);
  } else cells = arg.split(";").map((c) => c.split(",").map(Number));
  const s = 36;
  const w = Math.max(...cells.map((c) => c[0])) + 2;
  const h = Math.max(...cells.map((c) => c[1])) + 2;
  let out = "";
  for (let x = 0; x <= w; x++) out += `<line x1="${4 + x * s}" y1="4" x2="${4 + x * s}" y2="${4 + h * s}" stroke="#d9ccf5"/>`;
  for (let y = 0; y <= h; y++) out += `<line x1="4" y1="${4 + y * s}" x2="${4 + w * s}" y2="${4 + y * s}" stroke="#d9ccf5"/>`;
  out += cells.map(([x, y]) => `<rect x="${4 + (x + 0.5) * s}" y="${4 + (y + 0.5) * s}" width="${s}" height="${s}" fill="#a77bff" stroke="${C.line}" stroke-width="2"/>`).join("");
  return svg(w * s + 8, h * s + 8, out, "vis-area");
}

export function vis(code) {
  if (!code) return "";
  const i = code.indexOf(":");
  const kind = code.slice(0, i);
  const arg = code.slice(i + 1);
  switch (kind) {
    case "feld": return field(arg, 5);
    case "zf": return field(arg, 10);
    case "uhr": return clock(arg);
    case "geld": return money(arg);
    case "form": return shapes(arg);
    case "formen": return shapes(arg);
    case "mauer": return wall(arg);
    case "haus": return house(arg);
    case "menge": return amount(arg);
    case "reihe": return row(arg);
    case "strich": return tally(arg);
    case "lage": return place(arg);
    case "sym": return symmetry(arg);
    case "balken": return bars(arg);
    case "zug": return train(arg);
    case "st": return placeTable(arg, false);
    case "stp": return placeTable(arg, true);
    case "hze": return blocks(arg);
    case "strahl": return numberLine(arg);
    case "tafel": return thousandGrid(arg);
    case "kreuz": return malkreuz(arg);
    case "koerper": return solid(arg);
    case "netz": return net(arg);
    case "bau": return building(arg);
    case "linien": return lines(arg);
    case "flaeche": return area(arg);
    default: return `<span>${esc(code)}</span>`;
  }
}

// Kurze Beschreibung für Elternbereich und Auswertung
export function visText(code) {
  if (!code || !/^[a-z]+:/.test(code)) return code;
  const [kind, ...rest] = code.split(":");
  const arg = rest.join(":");
  if (kind === "uhr") {
    const [h, m = "00"] = arg.split(":");
    return `${h}:${String(m).padStart(2, "0")} Uhr`;
  }
  if (kind === "geld") return arg.split(",").map((v) => (Number(v) >= 1 ? `${v} €` : `${Math.round(Number(v) * 100)} ct`)).join(" + ");
  if (kind === "feld" || kind === "zf") return `${arg} Punkte`;
  if (kind === "menge") return arg.split("+").map((g) => g.split("*").reverse().join(" × ")).join(" + ");
  if (kind === "st" || kind === "stp") return `Stellentafel ${arg}`;
  if (kind === "hze") return `${arg} (Hunderter, Zehner, Einer)`;
  if (kind === "strahl") return `Zahlenstrahl ${arg.split(":")[0]} bis ${arg.split(":")[1]}`;
  if (kind === "koerper" || kind === "linien") return arg;
  if (kind === "netz") return "Netz";
  if (kind === "bau") return `Würfelgebäude ${arg}`;
  if (kind === "flaeche") return `Fläche ${arg}`;
  if (kind === "tafel") return `Tausendertafel ab ${arg.split(":")[0]}`;
  if (kind === "lage") return `${arg.split(":")[0]} ${arg.split(":")[1]}`;
  return arg;
}
