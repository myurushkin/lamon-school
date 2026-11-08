// Исследователи и предприниматели, с которыми мы работаем.
// Цитаты — перевод отзывов с broutonlab.com; оригиналы на английском сохранены в `quoteEn`.
export interface Partner {
  name: string;
  title: string;
  organization: string;
  country: string;
  photo?: string;
  href?: string;
  quote?: string;
  quoteEn?: string;
}

export const partners: Partner[] = [
  {
    name: "Clarence Lee",
    title: "Профессор цифрового маркетинга (ex-Cornell), основатель",
    organization: "Eisengard.ai",
    country: "США",
    photo: "/partners/clarence.webp",
    href: "https://eisengard.ai",
    quote: "Команда помогла автоматизировать наш рабочий процесс с помощью ИИ, и мы стали обрабатывать запросы клиентов заметно быстрее. Начать работу было легко, а результаты — выдающимися.",
    quoteEn: "BroutonLab team helped me automate our workflow with their AI development skills, and it sped up the rate at which we process our customers' requests. Getting started with them was easy, and the results were outstanding.",
  },
  {
    name: "Theodore Omtzigt, Ph.D.",
    title: "CEO",
    organization: "Stillwater Supercomputing",
    country: "США",
    photo: "/partners/theodore.webp",
    href: "https://stillwater-sc.com",
    quote: "Разработали бэкенд PyTorch для нестандартных числовых форматов в тесном сотрудничестве с нашими исследователями компиляторов. Рекомендую для сложных исследовательских проектов.",
    quoteEn: "BroutonLab developed a PyTorch backend for non-standard number formats, collaborating closely with our compiler researchers. Highly recommended for complex, research-driven projects.",
  },
  {
    name: "Reinaldo Scherner",
    title: "Основатель",
    organization: "SeedMetrics",
    country: "Бразилия",
    photo: "/partners/reinaldo.webp",
    href: "https://seedmetricslab.com",
    quote: "Рекомендую Михаила за выдающийся вклад как учёного по данным и бизнес-партнёра. Его видение и способность схватывать детали заметно повлияли на успех нашей команды.",
    quoteEn: "I highly recommend Michael for his outstanding contributions as a data scientist and business partner. His exceptional vision and ability to grasp intricate details have made a significant impact on our team's success.",
  },
  {
    name: "Константин",
    title: "TODO: фамилия, должность",
    organization: "TODO: университет или компания",
    country: "Китай",
  },
];
