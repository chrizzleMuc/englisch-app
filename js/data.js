// Feste Bausteine der App. Die Lerninhalte selbst stehen im Ordner "inhalte".

export const PROFILES = [
  { id: "entdecker", title: "Entdecker", pic: "🧭" },
  { id: "pirat", title: "Pirat", pic: "🏴‍☠️" }
];

export const PRAISE = ["Super!", "Toll gemacht!", "Klasse!", "Prima!", "Spitze!", "Genau!"];
export const PRAISE_EN = ["Great!", "Well done!", "Brilliant!", "Super!", "Fantastic!"];

// Bausteine für den Avatar. "en" wird beim Antippen vorgesprochen.
export const AVATAR = {
  base: [
    ["🐱", "cat"], ["🐶", "dog"], ["🦊", "fox"], ["🐼", "panda"], ["🐯", "tiger"], ["🦁", "lion"],
    ["🐸", "frog"], ["🐵", "monkey"], ["🦄", "unicorn"], ["🐲", "dragon"], ["🐧", "penguin"], ["🐨", "koala"],
    ["🐻", "bear"], ["🐰", "rabbit"], ["🐷", "pig"], ["🐮", "cow"], ["🐭", "mouse"], ["🦉", "owl"],
    ["🦜", "parrot"], ["🐙", "octopus"], ["🐢", "turtle"], ["🐬", "dolphin"], ["🦋", "butterfly"], ["🦖", "dinosaur"]
  ],
  color: [
    ["#ff8787", "red"], ["#74c0fc", "blue"], ["#8ce99a", "green"], ["#ffe066", "yellow"],
    ["#ffa94d", "orange"], ["#faa2c1", "pink"], ["#b197fc", "purple"], ["#d8a47f", "brown"]
  ]
};

export const LESSONS = [
  { icon: "🆕", title: "Neue Wörter" },
  { icon: "🎯", title: "Wörter üben" },
  { icon: "💬", title: "Sätze" },
  { icon: "📖", title: "Geschichte" },
  { icon: "🏆", title: "Abschluss" }
];

// Stimmlage pro Sprecher in den Geschichten
export const SPEAKERS = { Tom: { pitch: 0.85, pic: "👦" }, Lisa: { pitch: 1.35, pic: "👧" } };
