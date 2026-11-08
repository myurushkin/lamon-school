import { defineConfig } from "astro/config";

// Статическая сборка: `npm run build` кладёт готовые HTML в dist/.
export default defineConfig({
  site: "https://lamon.school",
  output: "static",
  trailingSlash: "ignore",
  build: { format: "directory" },
  server: { host: "127.0.0.1", port: 4321 },
});
