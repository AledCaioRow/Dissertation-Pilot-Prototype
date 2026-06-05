// Copies the local UMD bundles of React, ReactDOM and Babel-standalone into
// src/sandbox/vendor so they can be imported as raw text and injected into the
// C3 sandbox iframe. Runs automatically via the predev/prebuild npm hooks.
// Bundling locally (no CDN) is what lets the sandbox set connect-src 'none'.

import { mkdirSync, copyFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const dest = resolve(root, "src/sandbox/vendor");
mkdirSync(dest, { recursive: true });

const files = [
  ["react/umd/react.production.min.js", "react.production.min.js"],
  ["react-dom/umd/react-dom.production.min.js", "react-dom.production.min.js"],
  ["@babel/standalone/babel.min.js", "babel.min.js"],
];

for (const [src, name] of files) {
  const from = resolve(root, "node_modules", src);
  if (!existsSync(from)) {
    console.error(`[copy-vendor] missing ${from} — run npm install first`);
    process.exit(1);
  }
  copyFileSync(from, resolve(dest, name));
  console.log(`[copy-vendor] ${name}`);
}
