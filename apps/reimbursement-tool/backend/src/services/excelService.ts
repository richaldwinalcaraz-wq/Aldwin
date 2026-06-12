import * as XLSX from 'xlsx';
import * as fs from 'fs';
import * as path from 'path';
import { BillingRow, ProcessedRow } from '../types';

const HEADER_MAP: Record<string, keyof BillingRow> = {
  'company name': 'companyName',
  'company': 'companyName',
  'email': 'email',
  'ticket number': 'ticketNumber',
  'ticket #': 'ticketNumber',
  'notes': 'notes',
  'cc': 'cc',
  'bcc': 'bcc',
  'rate': 'rate',
  'currency': 'currency',
  'total': 'total',
  'converted usd': 'convertedUsd',
  'converted': 'convertedUsd',
  'total to charge': 'totalToCharge',
  'to carry over': 'toCarryOver',
  'carry over': 'toCarryOver',
  'btm': 'btm',
  'past due': 'pastDue',
  'report sent by': 'reportSentBy',
  'sent by': 'reportSentBy',
};

function normalizeHeader(h: string): string {
  return h.toString().trim().toLowerCase();
}

export function parseExcel(buffer: Buffer): BillingRow[] {
  const workbook = XLSX.read(buffer, { type: 'buffer', cellDates: true });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  const rawRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, {
    defval: '',
    raw: false,
  });

  if (rawRows.length === 0) return [];

  const headers = Object.keys(rawRows[0]);
  const headerIndexMap = new Map<string, string>();
  for (const h of headers) {
    const norm = normalizeHeader(h);
    headerIndexMap.set(norm, h);
  }

  return rawRows.map((row, idx): BillingRow => {
    const mapped: Partial<BillingRow> = {
      rowIndex: idx,
      _raw: { ...row },
    };

    for (const [norm, field] of Object.entries(HEADER_MAP)) {
      const originalKey = headerIndexMap.get(norm);
      if (originalKey && field !== '_raw' && field !== 'rowIndex') {
        (mapped as Record<string, unknown>)[field] = String(row[originalKey] ?? '').trim();
      }
    }

    return {
      rowIndex: idx,
      companyName: mapped.companyName ?? '',
      email: mapped.email ?? '',
      ticketNumber: mapped.ticketNumber ?? '',
      notes: mapped.notes ?? '',
      cc: mapped.cc ?? '',
      bcc: mapped.bcc ?? '',
      rate: mapped.rate ?? '',
      currency: mapped.currency ?? '',
      total: mapped.total ?? '',
      convertedUsd: mapped.convertedUsd ?? '',
      totalToCharge: mapped.totalToCharge ?? '',
      toCarryOver: mapped.toCarryOver ?? '',
      btm: mapped.btm ?? '',
      pastDue: mapped.pastDue ?? '',
      reportSentBy: mapped.reportSentBy ?? '',
      _raw: row,
    };
  });
}

export function generateWriteBack(
  originalBuffer: Buffer,
  processedRows: ProcessedRow[],
  exportDir: string
): string {
  const workbook = XLSX.read(originalBuffer, { type: 'buffer', cellDates: true });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];

  const range = XLSX.utils.decode_range(sheet['!ref'] ?? 'A1');
  const headerRow = 0;

  // Build header → col index map
  const headerColMap = new Map<string, number>();
  for (let c = range.s.c; c <= range.e.c; c++) {
    const cell = sheet[XLSX.utils.encode_cell({ r: headerRow, c })];
    if (cell?.v) {
      headerColMap.set(normalizeHeader(String(cell.v)), c);
    }
  }

  const writeBackColumns: Array<{ key: keyof ProcessedRow; header: string }> = [
    { key: 'hubspotTicketId', header: 'Ticket Number' },
    { key: 'sendStatus', header: 'SEND STATUS' },
    { key: 'dateSent', header: 'DATE SENT' },
    { key: 'emailSent', header: 'EMAIL SENT' },
    { key: 'processedBy', header: 'PROCESSED BY' },
    { key: 'errorLog', header: 'ERROR LOG' },
  ];

  // Ensure write-back columns exist (add if missing)
  let nextCol = range.e.c + 1;
  for (const col of writeBackColumns) {
    const normHeader = normalizeHeader(col.header);
    if (!headerColMap.has(normHeader)) {
      const cellAddr = XLSX.utils.encode_cell({ r: headerRow, c: nextCol });
      sheet[cellAddr] = { v: col.header, t: 's' };
      headerColMap.set(normHeader, nextCol);
      nextCol++;
    }
  }

  // Update range to include new columns
  const newRange = XLSX.utils.decode_range(sheet['!ref'] ?? 'A1');
  if (nextCol - 1 > newRange.e.c) {
    newRange.e.c = nextCol - 1;
    sheet['!ref'] = XLSX.utils.encode_range(newRange);
  }

  // Write processed values per row
  for (const row of processedRows) {
    const excelRow = row.rowIndex + 1; // +1 for header row

    for (const col of writeBackColumns) {
      const colIdx = headerColMap.get(normalizeHeader(col.header));
      if (colIdx === undefined) continue;

      const cellAddr = XLSX.utils.encode_cell({ r: excelRow, c: colIdx });
      let value: unknown = '';

      if (col.key === 'hubspotTicketId') {
        value = row.hubspotTicketId ?? row.ticketNumber ?? '';
      } else if (col.key === 'emailSent') {
        value = row.emailSent ? 'YES' : 'NO';
      } else {
        value = row[col.key] ?? '';
      }

      sheet[cellAddr] = { v: String(value), t: 's' };
    }
  }

  const now = new Date();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  const yyyy = now.getFullYear();
  const filename = `Updated_Billing_Report_${mm}_${dd}_${yyyy}.xlsx`;
  const outputPath = path.join(exportDir, filename);

  if (!fs.existsSync(exportDir)) {
    fs.mkdirSync(exportDir, { recursive: true });
  }

  XLSX.writeFile(workbook, outputPath);
  return filename;
}
