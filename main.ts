// main.ts — entrypoint for the news-image-20261121 poster (Concept A).
//
// The poster is fully rendered at build time by poster/build_poster_21nov.py
// and stored beside this file as entry.png. This program does no drawing and
// touches no network: it only publishes those exact bytes to the output
// directory the grader provides, so two runs always write identical bytes.
//
// Local run:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = new URL("./entry.png", import.meta.url);
if (!existsSync(source)) {
  throw new Error("entry.png missing beside main.ts — re-render with poster/build_poster_21nov.py first");
}
copyFileSync(source, join(outputDir, "entry.png"));
