// Entry point for the make.fun news-image-20261121 bounty (v4).
// The front page is rendered offline by poster/build_poster_v4.py into
// entry.png; this file copies that image into the output directory
// expected by the grader, unchanged, so the run is fully deterministic.

import { copyFileSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(here, "output");

if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}

copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
console.log("wrote", join(outDir, "entry.png"));
