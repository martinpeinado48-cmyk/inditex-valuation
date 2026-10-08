// Renderiza fotogramas sueltos a PNG para revisar el diseño: node scripts/stills.mjs <carpeta> <frame> <frame> ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const [outDir, ...frames] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "InditexVideo" });
for (const f of frames) {
  const output = path.join(outDir, `f${String(f).padStart(4, "0")}.png`);
  await renderStill({ composition, serveUrl, frame: Number(f), output, imageFormat: "png" });
  console.log("ok", output);
}
