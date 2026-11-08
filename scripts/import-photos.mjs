import sharp from "sharp";
const SRC = "/home/myurushkin/shared/school";
const OUT = "/home/myurushkin/projects/school-workspace/site/public";
const jobs = [
  // блог EMNLP
  { in: `${SRC}/emnlp/IMG_0739.PNG`, out: `${OUT}/images/blog/emnlp-2026/cover.webp`, w: 1400 },
  { in: `${SRC}/emnlp/IMG_0737.PNG`, out: `${OUT}/images/blog/emnlp-2026/hall.webp`, w: 1600 },
  { in: `${SRC}/emnlp/IMG_0738.PNG`, out: `${OUT}/images/blog/emnlp-2026/ilya-poster.webp`, w: 1400 },
  { in: `${SRC}/emnlp/IMG_0742.PNG`, out: `${OUT}/images/blog/emnlp-2026/ilya-budapest.webp`, w: 1600 },
  { in: `${SRC}/emnlp/IMG_0815.PNG`, out: `${OUT}/images/blog/emnlp-2026/mikhail-budapest.webp`, w: 1400 },
];
for (const j of jobs) {
  const info = await sharp(j.in).rotate().resize({ width: j.w, withoutEnlargement: true }).webp({ quality: 82 }).toFile(j.out);
  console.log(j.out.split("/public")[1], info.width + "x" + info.height, Math.round(info.size / 1024) + " KB");
}
// портрет Ильи: квадрат, кадр по верху
const i = await sharp(`${SRC}/checkin_ilya.png`).rotate().resize({ width: 600, height: 600, fit: "cover", position: "top" }).webp({ quality: 85 }).toFile(`${OUT}/people/ilya.webp`);
console.log("/people/ilya.webp", i.width + "x" + i.height, Math.round(i.size / 1024) + " KB");
