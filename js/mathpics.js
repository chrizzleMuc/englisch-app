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
  if (kind === "lage") return `${arg.split(":")[0]} ${arg.split(":")[1]}`;
  return arg;
}
