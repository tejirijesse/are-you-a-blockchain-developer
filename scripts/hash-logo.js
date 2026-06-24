const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const logoPath = path.resolve(process.cwd(), "alu-logo.png");

if (!fs.existsSync(logoPath)) {
  console.error(`Missing logo file at ${logoPath}`);
  console.error("Add the real ALU logo file as alu-logo.png, then rerun npm run hash:logo.");
  process.exit(1);
}

const fileBuffer = fs.readFileSync(logoPath);
const hash = crypto.createHash("sha256").update(fileBuffer).digest("hex");

console.log(`SHA-256: ${hash}`);
console.log(`bytes32: 0x${hash}`);
