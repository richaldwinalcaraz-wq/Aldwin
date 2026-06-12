/**
 * Generates assets/icon.png (256x256) and assets/icon.ico from public/logo.svg
 * Run: node scripts/generate-icon.js
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const SVG_PATH = path.join(__dirname, '../public/logo.svg');
const ASSETS_DIR = path.join(__dirname, '../assets');
const PNG_PATH = path.join(ASSETS_DIR, 'icon.png');
const ICO_PATH = path.join(ASSETS_DIR, 'icon.ico');

if (!fs.existsSync(ASSETS_DIR)) fs.mkdirSync(ASSETS_DIR, { recursive: true });

const svgBuffer = fs.readFileSync(SVG_PATH);

async function run() {
  // Generate PNG at 256x256
  await sharp(svgBuffer)
    .resize(256, 256)
    .png()
    .toFile(PNG_PATH);
  console.log('Generated:', PNG_PATH);

  // Generate all ICO sizes as individual PNGs then pack
  const sizes = [16, 32, 48, 64, 128, 256];
  const pngBuffers = await Promise.all(
    sizes.map((s) =>
      sharp(svgBuffer).resize(s, s).png().toBuffer()
    )
  );

  // Build ICO manually (ICONDIR + ICONDIRENTRY headers + PNG data)
  const icoBuffer = buildIco(pngBuffers, sizes);
  fs.writeFileSync(ICO_PATH, icoBuffer);
  console.log('Generated:', ICO_PATH);
  console.log('Done. Update desktop shortcut to use:', ICO_PATH);
}

function buildIco(pngBuffers, sizes) {
  const count = pngBuffers.length;
  // ICONDIR: 6 bytes. ICONDIRENTRY: 16 bytes each. Data starts after header.
  const headerSize = 6 + 16 * count;
  let offset = headerSize;

  const headerBuf = Buffer.alloc(headerSize);
  headerBuf.writeUInt16LE(0, 0);     // reserved
  headerBuf.writeUInt16LE(1, 2);     // type: 1 = ICO
  headerBuf.writeUInt16LE(count, 4); // image count

  for (let i = 0; i < count; i++) {
    const size = sizes[i];
    const imgBuf = pngBuffers[i];
    const entryOffset = 6 + 16 * i;
    headerBuf.writeUInt8(size === 256 ? 0 : size, entryOffset);      // width (0 = 256)
    headerBuf.writeUInt8(size === 256 ? 0 : size, entryOffset + 1);  // height (0 = 256)
    headerBuf.writeUInt8(0, entryOffset + 2);   // color count
    headerBuf.writeUInt8(0, entryOffset + 3);   // reserved
    headerBuf.writeUInt16LE(1, entryOffset + 4); // planes
    headerBuf.writeUInt16LE(32, entryOffset + 6); // bit count
    headerBuf.writeUInt32LE(imgBuf.length, entryOffset + 8);  // size of image data
    headerBuf.writeUInt32LE(offset, entryOffset + 12); // offset to image data
    offset += imgBuf.length;
  }

  return Buffer.concat([headerBuf, ...pngBuffers]);
}

run().catch(console.error);
