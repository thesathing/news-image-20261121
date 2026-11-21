// v2 entrypoint: publish the pre-rendered poster to the output directory.
// The image is fully drawn at build time by poster/build_poster_v2.py;
// this program does no drawing and makes no network calls, it only
// copies those exact bytes, so two runs always write identical bytes.
//
// Local check:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = join(here, "entry.png");

if (!existsSync(src)) {
  throw new Error(
    "entry.png missing beside main.ts — render it first with poster/build_poster_v2.py",
  );
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
console.log("copied entry.png to " + join(outDir, "entry.png"));
