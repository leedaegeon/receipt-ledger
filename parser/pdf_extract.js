const fs = require('fs');
const pdfParse = require('pdf-parse');

async function main() {
const file = process.argv[2];
if (!file) {
console.error('Usage: node pdf_extract.js <file.pdf>');
process.exit(1);
}

const data = fs.readFileSync(file);
const out = await pdfParse(data);
process.stdout.write(out.text || '');
}

main().catch((e) => {
console.error(e?.message || String(e));
process.exit(1);
});
