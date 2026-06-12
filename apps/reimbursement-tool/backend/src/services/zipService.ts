import AdmZip from 'adm-zip';
import * as fs from 'fs';
import * as path from 'path';

function normalizeName(name: string): string {
  return name
    .toLowerCase()
    .replace(/\.[^/.]+$/, '') // strip extension
    .replace(/[^a-z0-9]/g, '') // strip non-alphanumeric
    .trim();
}

export function extractZipAndIndex(
  zipPath: string,
  extractDir: string
): Map<string, string> {
  if (!fs.existsSync(extractDir)) {
    fs.mkdirSync(extractDir, { recursive: true });
  }

  const zip = new AdmZip(zipPath);
  const entries = zip.getEntries();

  const pdfIndex = new Map<string, string>();

  for (const entry of entries) {
    if (entry.isDirectory) continue;
    if (!entry.entryName.toLowerCase().endsWith('.pdf')) continue;

    const basename = path.basename(entry.entryName);
    const outputPath = path.join(extractDir, basename);

    // Extract file
    fs.writeFileSync(outputPath, entry.getData());

    // Index by normalized name
    const normalizedKey = normalizeName(basename);
    pdfIndex.set(normalizedKey, outputPath);
  }

  return pdfIndex;
}

export function findPdfForCompany(
  companyName: string,
  pdfIndex: Map<string, string>
): { filename: string; path: string } | null {
  const normalizedCompany = normalizeName(companyName);

  // Exact match first
  for (const [key, filePath] of pdfIndex.entries()) {
    if (key === normalizedCompany) {
      return { filename: path.basename(filePath), path: filePath };
    }
  }

  // Partial match: company name contained in PDF filename
  for (const [key, filePath] of pdfIndex.entries()) {
    if (key.includes(normalizedCompany) || normalizedCompany.includes(key)) {
      return { filename: path.basename(filePath), path: filePath };
    }
  }

  return null;
}

export function validateZip(zipPath: string): { valid: boolean; error?: string } {
  try {
    const zip = new AdmZip(zipPath);
    const entries = zip.getEntries();
    const pdfCount = entries.filter(
      (e) => !e.isDirectory && e.entryName.toLowerCase().endsWith('.pdf')
    ).length;
    if (pdfCount === 0) {
      return { valid: false, error: 'ZIP contains no PDF files' };
    }
    return { valid: true };
  } catch (err) {
    return { valid: false, error: 'Invalid or corrupted ZIP file' };
  }
}
