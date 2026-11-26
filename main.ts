const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const maxBytes = 1 << 20;
const side = 1024;

function makeEdition(): Buffer {
  const venv = path.resolve(__dirname, "../build-venv/bin/python");
  const python = fs.existsSync(venv) ? venv : "python3";
  const renderer = path.join(__dirname, "build_image.py");
  const result = spawnSync(python, ["-IB", renderer], {
    maxBuffer: maxBytes,
    stdio: ["ignore", "pipe", "inherit"],
  });

  if (result.status === 69 || result.error?.code === "ENOENT") {
    // The standard-library-only contest runner can serve the built edition.
    return fs.readFileSync(path.join(__dirname, "entry.png"));
  }
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`Edition rendering failed (${result.signal ?? result.status})`);
  }
  return result.stdout;
}

const edition = makeEdition();
if (
  edition.length < 45 ||
  edition.length > maxBytes ||
  edition.toString("hex", 0, 16) !== "89504e470d0a1a0a0000000d49484452" ||
  edition.readUInt32BE(16) !== side ||
  edition.readUInt32BE(20) !== side
) {
  throw new Error("The edition must be a 1024 × 1024 PNG of at most 1 MiB.");
}

const output = path.resolve(process.env.MAKEFUN_OUTPUT_DIR || "/output");
fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(path.join(output, "entry.png"), edition);
