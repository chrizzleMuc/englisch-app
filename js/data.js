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
  { id: "colours", title: "Farben", pic: "🎨", color: "#a55eea", type: "words", items: [
      { en: "red", de: "rot", pic: "🟥" },
      { en: "blue", de: "blau", pic: "🟦" },
      { en: "green", de: "grün", pic: "🟩" },
      { en: "yellow", de: "gelb", pic: "🟨" },
      { en: "orange", de: "orange", pic: "🟧" },
      { en: "purple", de: "lila", pic: "🟪" },
      { en: "brown", de: "braun", pic: "🟫" },
      { en: "black", de: "schwarz", pic: "⬛" },
      { en: "white", de: "weiß", pic: "⬜" },
      { en: "pink", de: "rosa", pic: "🩷" }
    ]
  },
  { id: "numbers", title: "Zahlen", pic: "🔢", color: "#3498db", type: "words", items: [
      { en: "one", de: "eins", pic: "1️⃣" },
      { en: "two", de: "zwei", pic: "2️⃣" },
      { en: "three", de: "drei", pic: "3️⃣" },
      { en: "four", de: "vier", pic: "4️⃣" },
      { en: "five", de: "fünf", pic: "5️⃣" },
      { en: "six", de: "sechs", pic: "6️⃣" },
      { en: "seven", de: "sieben", pic: "7️⃣" },
      { en: "eight", de: "acht", pic: "8️⃣" },
      { en: "nine", de: "neun", pic: "9️⃣" },
      { en: "ten", de: "zehn", pic: "🔟" }
    ]
  },
  { id: "food", title: "Essen", pic: "🍎", color: "#e74c3c", type: "words", items: [
      { en: "apple", de: "Apfel", pic: "🍎" },
      { en: "banana", de: "Banane", pic: "🍌" },
      { en: "bread", de: "Brot", pic: "🍞" },
      { en: "milk", de: "Milch", pic: "🥛" },
      { en: "cheese", de: "Käse", pic: "🧀" },
      { en: "egg", de: "Ei", pic: "🥚" },
      { en: "water", de: "Wasser", pic: "💧" },
      { en: "cake", de: "Kuchen", pic: "🍰" },
      { en: "biscuit", de: "Keks", pic: "🍪" },
      { en: "ice cream", de: "Eis", pic: "🍦" },
      { en: "carrot", de: "Karotte", pic: "🥕" },
      { en: "pizza", de: "Pizza", pic: "🍕" }
    ]
  },
  { id: "home", title: "Zuhause", pic: "🏠", color: "#e67e22", type: "words", items: [
      { en: "house", de: "Haus", pic: "🏠" },
      { en: "bed", de: "Bett", pic: "🛏️" },
      { en: "chair", de: "Stuhl", pic: "🪑" },
      { en: "door", de: "Tür", pic: "🚪" },
      { en: "sofa", de: "Sofa", pic: "🛋️" },
      { en: "bath", de: "Badewanne", pic: "🛁" },
      { en: "toothbrush", de: "Zahnbürste", pic: "🪥" },
      { en: "lamp", de: "Lampe", pic: "💡" },
      { en: "clock", de: "Uhr", pic: "⏰" },
      { en: "key", de: "Schlüssel", pic: "🔑" }
    ]
  },
  { id: "play", title: "Spielen", pic: "⚽", color: "#1abc9c", type: "words", items: [
      { en: "ball", de: "Ball", pic: "⚽" },
      { en: "teddy", de: "Teddy", pic: "🧸" },
      { en: "kite", de: "Drachen", pic: "🪁" },
      { en: "puzzle", de: "Puzzle", pic: "🧩" },
      { en: "balloon", de: "Luftballon", pic: "🎈" },
      { en: "bike", de: "Fahrrad", pic: "🚲" },
      { en: "car", de: "Auto", pic: "🚗" },
      { en: "friend", de: "Freund", pic: "🧑‍🤝‍🧑" },
      { en: "dice", de: "Würfel", pic: "🎲" },
      { en: "book", de: "Buch", pic: "📖" }
    ]
  }
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
    ["🐻", "bear"], ["🐰", "rabbit"], ["🐷", "pig"], ["🐮", "cow"], ["🐭", "mouse"], ["🦉", "owl"],
    ["🦜", "parrot"], ["🐙", "octopus"], ["🐢", "turtle"], ["🐬", "dolphin"], ["🦋", "butterfly"], ["🦖", "dinosaur"]
  ],
  color: [
    ["#ff8787", "red"], ["#74c0fc", "blue"], ["#8ce99a", "green"], ["#ffe066", "yellow"],
    ["#ffa94d", "orange"], ["#faa2c1", "pink"], ["#b197fc", "purple"], ["#d8a47f", "brown"]
  ]
};

// Fächer. Neue Fächer bekommen hier einen Eintrag mit eigener Themenliste.
export const SUBJECTS = [
  { id: "englisch", title: "Englisch", pic: "🇬🇧", color: "#ff9f43", topics: TOPICS }
];
