// Преподаватели Lamon. Поля с TODO — заполнить реальными данными.
export interface TeamMember {
  id: string;
  name: string;
  role: string;
  bio: string;
  regalia: string[];   // буллеты, как на shad.yandex.ru/teachers
  teaches: string[];   // теги направлений
  photo?: string; // /people/<file>.webp
  initials: string;
  links?: { label: string; href: string }[];
}

export const team: TeamMember[] = [
  {
    id: "yurushkin",
    name: "Юрушкин Михаил Викторович",
    role: "Руководитель школы",
    bio: "",
    regalia: [
      "кандидат физико-математических наук",
      "доцент мехмата ЮФУ",
      "основатель и руководитель ИИ-компании BroutonLab",
      "больше 15 лет пишет код, который работает в продакшене",
    ],
    teaches: ["генеративный ИИ", "ИИ-стартап"],
    photo: "/people/michael.webp",
    initials: "МЮ",
  },
  {
    id: "bachurin",
    name: "Бачурин Станислав Сергеевич",
    role: "Биомоделирование",
    bio: "",
    regalia: [
      "TODO: степень и должность",
      "работает на стыке математики, квантовой химии и биологии",
      "ИИ- и автоматные методы для поиска неканонических структур ДНК и тандемных повторов",
      "соавтор статей в Biochemical and Biophysical Research Communications (2024) и Computational Biology and Chemistry (2019), Elsevier",
    ],
    teaches: ["поиск лекарства от рака"],
    initials: "СБ",
  },
  {
    id: "chekin",
    name: "Чекин Илья Сергеевич",
    photo: "/people/ilya.webp",
    role: "Исследования в NLP",
    bio: "",
    regalia: [
      "аспирант мехмата ЮФУ",
      "соавтор статьи на EMNLP 2026, Industry Track",
    ],
    teaches: ["генеративный ИИ"],
    initials: "ИЧ",
  },
];
