// Erzeugt die Weltkarten für den Sachunterricht aus Natural-Earth-Daten (gemeinfrei),
// Paket world-atlas@2.0.2 (countries-110m.json) und topojson-client@3.1.0.
//   node werkzeug/gen_weltkarte.js <pfad-zu-world-atlas> <pfad-zu-topojson-client.js>
// Ergebnis: img/zeichnungen/weltkarte.svg (alle Kontinente bunt) und weltkarte-<kontinent>.svg (einer hervorgehoben)
const fs = require("fs");
const [atlasDir, tcFile] = process.argv.slice(2);
const topojson = require(tcFile);
const world = JSON.parse(fs.readFileSync(atlasDir + "/countries-110m.json", "utf8"));
const feats = topojson.feature(world, world.objects.countries).features;

const W = 1000, LAT0 = 84, LAT1 = -74, H = Math.round(W * (LAT0 - LAT1) / 360);
const X = (lon) => ((lon + 180) / 360) * W;
const Y = (lat) => ((LAT0 - lat) / (LAT0 - LAT1)) * H;
const COL = { nordamerika: "#38a8e8", suedamerika: "#f6cf4a", europa: "#f08cb4", afrika: "#f59a35", asien: "#a95fb4", australien: "#2bb59a", antarktis: "#ffffff" };

function centroid(geom) {
  // Mittelpunkt des größten Rings
  const polys = geom.type === "Polygon" ? [geom.coordinates] : geom.coordinates;
  let best = null, bestA = -1;
  for (const p of polys) {
    const r = p[0];
    let a = 0, cx = 0, cy = 0;
    for (let i = 0; i < r.length - 1; i++) {
      const [x1, y1] = r[i], [x2, y2] = r[i + 1];
      const c = x1 * y2 - x2 * y1;
      a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c;
    }
    if (Math.abs(a) > bestA) { bestA = Math.abs(a); best = [cx / (3 * a), cy / (3 * a)]; }
  }
  return best;
}
const ASIA = new Set(["792", "268", "051", "031", "398", "196"]); // Türkei, Georgien, Armenien, Aserbaidschan, Kasachstan, Zypern
const AFRICA = new Set(["232"]); // Eritrea
const NA = new Set(["591", "188"]);
function continent(f) {
  const [lon, lat] = centroid(f.geometry);
  const id = String(f.id).padStart(3, "0");
  if (id === "010" || lat < -60) return "antarktis";
  if (id === "643") return "russland";
  if (lon < -25) return lat < 12.5 && lon > -82 && !NA.has(id) ? "suedamerika" : "nordamerika";
  if (AFRICA.has(id)) return "afrika";
  if (ASIA.has(id)) return "asien";
  if (lon > -20 && lon < 52 && lat > -36 && lat < 37.5 && !(lon > 34.5 && lat > 12.5)) return "afrika";
  if (lat > 35 && lon > -25 && lon < 45) return "europa";
  if (lon > 112 && lat < -1 && id !== "360" && id !== "626") return "australien";
  return "asien";
}
function pathOf(geom) {
  const polys = geom.type === "Polygon" ? [geom.coordinates] : geom.coordinates;
  let d = "";
  for (const p of polys) for (let r of p) {
    if (r.some(([lo]) => lo > 170) && r.some(([lo]) => lo < -170)) r = r.map(([lo, la]) => [lo < 0 ? lo + 360 : lo, la]);
    let prev = null;
    r.forEach(([lon, lat], i) => {
      // Sprung über die Datumsgrenze: neu ansetzen
      d += (i === 0 || (prev !== null && Math.abs(lon - prev) > 180) ? "M" : "L") + X(lon).toFixed(1) + "," + Y(Math.max(lat, LAT1 - 5)).toFixed(1);
      prev = lon;
    });
    d += "Z";
  }
  return d;
}
const groups = {};
for (const f of feats) {
  const polys = f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates;
  for (const p of polys) {
    const g = { type: "Polygon", coordinates: p };
    const c = continent({ id: f.id, geometry: g });
    (groups[c] = groups[c] || []).push(pathOf(g));
  }
}
const ural = X(58);
function map(highlight) {
  const fill = (c) => (highlight ? (c === highlight ? (c === "antarktis" ? "#4fb3e8" : COL[c]) : "#b9c3cc") : COL[c]);
  let s = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}"><defs><clipPath id="eu"><rect x="0" y="0" width="${ural}" height="${H}"/></clipPath><clipPath id="as"><rect x="${ural}" y="0" width="${W}" height="${H}"/></clipPath></defs>`;
  s += `<rect width="${W}" height="${H}" fill="#d9eefb"/>`;
  for (const [c, ps] of Object.entries(groups)) {
    if (c === "russland") continue;
    s += `<path d="${ps.join("")}" fill="${fill(c)}" stroke="${c === "antarktis" ? "#9fb3c4" : fill(c)}" stroke-width="${c === "antarktis" ? 1.2 : 0.8}" stroke-linejoin="round"/>`;
  }
  const ru = groups.russland.join("");
  s += `<path d="${ru}" fill="${fill("europa")}" stroke="${fill("europa")}" stroke-width="0.8" clip-path="url(#eu)"/><path d="${ru}" fill="${fill("asien")}" stroke="${fill("asien")}" stroke-width="0.8" clip-path="url(#as)"/>`;
  return s + "</svg>";
}
const out = "img/zeichnungen";
fs.writeFileSync(`${out}/weltkarte.svg`, map(null));
for (const c of Object.keys(COL)) fs.writeFileSync(`${out}/weltkarte-${c}.svg`, map(c));
console.log("Weltkarte", W, "x", H, Object.fromEntries(Object.entries(groups).map(([k, v]) => [k, v.length])));
