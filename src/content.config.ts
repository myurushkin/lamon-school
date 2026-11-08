import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

// Записи блога: src/content/blog/<slug>.md
// Фото кладём в public/images/blog/<slug>/ и указываем путь в cover.
const blog = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    description: z.string().max(200),
    date: z.coerce.date(),
    cover: z.string(),            // /images/blog/<slug>/cover.jpg
    coverAlt: z.string(),
    place: z.string().optional(), // «Будапешт», «Ростов-на-Дону»
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false), // показывать как «последний кейс» на главной
    heroTitle: z.string().optional(),      // заголовок кейса на главной (если отличается от title)
    heroText: z.string().optional(),       // подводка кейса на главной
    paperUrl: z.string().url().optional(), // ссылка на работу
    paperTitle: z.string().optional(),
    gallery: z
      .array(z.object({ src: z.string(), alt: z.string(), caption: z.string().optional() }))
      .default([]),
  }),
});

export const collections = { blog };
