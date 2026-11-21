// Copy entry.png into the make.fun output directory.
// No network, no drawing: a plain file copy.
import { copyFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const src = join(here, "entry.png");
const dest = join(outDir, "entry.png");

if (!existsSync(src)) {
  console.error("entry.png not found next to main.ts: " + src);
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, dest);
console.log("copied entry.png to " + dest);
