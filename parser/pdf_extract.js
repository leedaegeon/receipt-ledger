const fs = require('fs');
const { PDFParse } = require('pdf-parse');

async function main() {
  const file = process.argv[2];
  if (!file) {
    console.error('Usage: node pdf_extract.js <file.pdf>');
    process.exit(1);
  }

  const data = fs.readFileSync(file);
  const parser = new PDFParse({ data });
  try {
    const out = await parser.getText();
    process.stdout.write(out.text || '');
  } finally {
    await parser.destroy();
  }
}

main().catch((e) => {
  console.error(e?.message || String(e));
  process.exit(1);
});
