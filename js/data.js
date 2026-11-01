// Inhalte von Learnino.
// Neue Themen oder Wörter hier ergänzen. "en" wird vorgesprochen (britisches Englisch),
// "de" ist die deutsche Bedeutung, "pic" das Bild (Emoji).
// Bei Redewendungen beschreibt "situation" auf Deutsch, wann man den Satz benutzt.

export const TOPICS = [
  {
    id: "phrases",
    title: "Hallo & Tschüss",
    pic: "👋",
    color: "#ff9f43",
    type: "phrases",
    items: [
      { en: "Hello!", de: "Hallo!", pic: "👋", situation: "Du triffst deine Freundin auf dem Spielplatz. Was sagst du?" },
      { en: "Goodbye!", de: "Auf Wiedersehen!", pic: "🚪", situation: "Du gehst nach Hause. Was sagst du zum Abschied?" },
      { en: "Good morning!", de: "Guten Morgen!", pic: "🌅", situation: "Es ist früh am Morgen. Was sagst du?" },
      { en: "Bye!", de: "Tschüss!", pic: "🙋", situation: "Du verabschiedest dich ganz kurz und locker. Was sagst du?" },
      { en: "What's your name?", de: "Wie heißt du?", pic: "❓", situation: "Du willst wissen, wie ein anderes Kind heißt. Was fragst du?" },
      { en: "My name is {name}.", de: "Ich heiße {name}.", pic: "😊", situation: "Jemand fragt dich nach deinem Namen. Was antwortest du?" },
      { en: "I am {age}.", de: "Ich bin {age_de} Jahre alt.", pic: "🎂", situation: "Jemand fragt, wie alt du bist. Was antwortest du?" },
      { en: "How are you?", de: "Wie geht es dir?", pic: "🤔", situation: "Du willst wissen, wie es deinem Freund geht. Was fragst du?" },
      { en: "I'm fine, thank you.", de: "Mir geht es gut, danke.", pic: "👍", situation: "Jemand fragt, wie es dir geht. Dir geht es gut. Was antwortest du?" },
      { en: "Please.", de: "Bitte.", pic: "🙏", situation: "Du möchtest etwas haben und bist höflich. Was sagst du?" },
      { en: "Thank you.", de: "Danke.", pic: "💝", situation: "Du bekommst ein Geschenk. Was sagst du?" },
      { en: "Let's play!", de: "Lass uns spielen!", pic: "🤸", situation: "Du willst mit einem Kind spielen. Was sagst du?" }
    ]
  },
  {
    id: "animals",
    title: "Tiere",
    pic: "🐶",
    color: "#2ecc71",
    type: "words",
    items: [
      { en: "cat", de: "Katze", pic: "🐱" },
      { en: "dog", de: "Hund", pic: "🐶" },
      { en: "bird", de: "Vogel", pic: "🐦" },
      { en: "fish", de: "Fisch", pic: "🐟" },
      { en: "horse", de: "Pferd", pic: "🐴" },
      { en: "cow", de: "Kuh", pic: "🐮" },
      { en: "pig", de: "Schwein", pic: "🐷" },
      { en: "mouse", de: "Maus", pic: "🐭" },
      { en: "rabbit", de: "Hase", pic: "🐰" },
      { en: "duck", de: "Ente", pic: "🦆" },
      { en: "lion", de: "Löwe", pic: "🦁" },
      { en: "frog", de: "Frosch", pic: "🐸" }
    ]
  },
  { id: "colours", title: "Farben", pic: "🎨", color: "#a55eea", type: "words", soon: true, items: [] },
  { id: "numbers", title: "Zahlen", pic: "🔢", color: "#3498db", type: "words", soon: true, items: [] },
  { id: "food", title: "Essen", pic: "🍎", color: "#e74c3c", type: "words", soon: true, items: [] },
  { id: "home", title: "Zuhause", pic: "🏠", color: "#e67e22", type: "words", soon: true, items: [] },
  { id: "play", title: "Spielen", pic: "⚽", color: "#1abc9c", type: "words", soon: true, items: [] }
];

export const PROFILES = [
  { id: "entdecker", title: "Entdecker", pic: "🧭", age: 7, reads: false, perLesson: 4 },
  { id: "pirat", title: "Pirat", pic: "🏴‍☠️", age: 9, reads: true, perLesson: 6 }
];

export const NUMBER_WORDS = { 7: ["seven", "sieben"], 8: ["eight", "acht"], 9: ["nine", "neun"], 10: ["ten", "zehn"] };

export const PRAISE = ["Super!", "Toll gemacht!", "Klasse!", "Prima!", "Spitze!", "Genau!"];
export const PRAISE_EN = ["Great!", "Well done!", "Brilliant!", "Super!", "Fantastic!"];

// Bausteine für den Avatar. "en" wird beim Antippen vorgesprochen.
export const AVATAR = {
  base: [
    ["🐱", "cat"], ["🐶", "dog"], ["🦊", "fox"], ["🐼", "panda"], ["🐯", "tiger"], ["🦁", "lion"],
    ["🐸", "frog"], ["🐵", "monkey"], ["🦄", "unicorn"], ["🐲", "dragon"], ["🐧", "penguin"], ["🐨", "koala"],
    ["🦜", "parrot"], ["🐙", "octopus"], ["🤖", "robot"], ["👽", "alien"], ["👧", "girl"], ["👦", "boy"],
    ["🧚", "fairy"], ["🧜", "mermaid"], ["🦸", "superhero"], ["🧙", "wizard"]
  ],
  hat: [
    ["", "no hat"], ["👑", "crown"], ["🎩", "top hat"], ["🧢", "cap"], ["🎀", "bow"], ["🌸", "flower"], ["⭐", "star"], ["🎓", "school hat"]
  ],
  item: [
    ["", "nothing"], ["⚽", "ball"], ["🎈", "balloon"], ["🧸", "teddy"], ["🍭", "lollipop"], ["🪁", "kite"],
    ["🌈", "rainbow"], ["🔭", "telescope"], ["🧭", "compass"], ["🗺️", "map"], ["🦴", "bone"], ["🍕", "pizza"]
  ],
  color: [
    ["#ff8787", "red"], ["#74c0fc", "blue"], ["#8ce99a", "green"], ["#ffe066", "yellow"],
    ["#ffa94d", "orange"], ["#faa2c1", "pink"], ["#b197fc", "purple"], ["#d8a47f", "brown"]
  ]
};
