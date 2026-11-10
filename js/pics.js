// 3D-Bilder (Microsoft Fluent Emoji, MIT-Lizenz) statt der flachen Emojis des Geräts.
// Zeichen ohne Bild in img/emoji werden weiter als normales Emoji angezeigt.
const MAP = {"1️⃣": "31-20e3", "2️⃣": "32-20e3", "3️⃣": "33-20e3", "4️⃣": "34-20e3", "5️⃣": "35-20e3", "6️⃣": "36-20e3", "7️⃣": "37-20e3", "8️⃣": "38-20e3", "9️⃣": "39-20e3", "✅": "2705", "❌": "274c", "❓": "2753", "❤️": "2764", "⬛": "2b1b", "⬜": "2b1c", "⭐": "2b50", "🌙": "1f319", "🌞": "1f31e", "🌻": "1f33b", "🍌": "1f34c", "🍎": "1f34e", "🍓": "1f353", "🍽️": "1f37d", "🎁": "1f381", "🎂": "1f382", "🎄": "1f384", "🎈": "1f388", "🎉": "1f389", "🎨": "1f3a8", "🏠": "1f3e0", "🐑": "1f411", "🐟": "1f41f", "🐦": "1f426", "🐭": "1f42d", "🐮": "1f42e", "🐰": "1f430", "🐱": "1f431", "🐴": "1f434", "🐶": "1f436", "🐷": "1f437", "👀": "1f440", "👂": "1f442", "👃": "1f443", "👄": "1f444", "👈": "1f448", "👉": "1f449", "👋": "1f44b", "👏": "1f44f", "👐": "1f450", "👦": "1f466", "👧": "1f467", "👻": "1f47b", "💝": "1f49d", "💥": "1f4a5", "💪": "1f4aa", "💬": "1f4ac", "🔁": "1f501", "🔟": "1f51f", "🔴": "1f534", "🕯️": "1f56f", "🖐️": "1f590", "😀": "1f600", "😂": "1f602", "😊": "1f60a", "😋": "1f60b", "😠": "1f620", "😢": "1f622", "😱": "1f631", "😴": "1f634", "🙂": "1f642", "🙌": "1f64c", "🙏": "1f64f", "🟥": "1f7e5", "🟦": "1f7e6", "🟧": "1f7e7", "🟨": "1f7e8", "🟩": "1f7e9", "🟪": "1f7ea", "🟫": "1f7eb", "🦆": "1f986", "🦇": "1f987", "🦵": "1f9b5", "🦶": "1f9b6", "🧙‍♀️": "1f9d9-200d-2640", "🩷": "1fa77", "🫐": "1fad0", "🎃": "1f383", "😍": "1f60d"};

const seg = typeof Intl !== "undefined" && Intl.Segmenter ? new Intl.Segmenter("de", { granularity: "grapheme" }) : null;

function parts(s) {
  return seg ? [...seg.segment(s)].map((x) => x.segment) : [...s];
}

export function pic(s) {
  if (!s) return "";
  return parts(String(s))
    .map((g) => {
      const code = MAP[g] || MAP[g.replace(/\uFE0F/g, "")];
      return code ? `<img class="emo" src="img/emoji/${code}.webp" alt="" draggable="false">` : `<span class="emo-txt">${g}</span>`;
    })
    .join("");
}

export const PIC_FILES = Object.values(MAP).map((c) => `img/emoji/${c}.webp`);
