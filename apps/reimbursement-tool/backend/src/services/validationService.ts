import { BillingRow, ValidationResult, ValidationStatus, ProcessedRow } from '../types';
import { findPdfForCompany } from './zipService';

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}$/;
const EMAIL_EXTRACT_REGEX = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}/g;

export function isValidEmail(email: string): boolean {
  return EMAIL_REGEX.test(email.trim());
}

export function parseEmailList(raw: string): string[] {
  if (!raw || !raw.trim()) return [];
  const matches = raw.match(EMAIL_EXTRACT_REGEX);
  return matches ?? [];
}

export function validateRow(
  row: BillingRow,
  pdfIndex: Map<string, string>
): ValidationResult {
  const errors: string[] = [];

  const notes = row.notes.trim().toLowerCase();
  const isNoAccess = notes === 'no access';

  if (!row.companyName.trim()) {
    errors.push('Missing company name');
  }

  if (!row.email.trim()) {
    errors.push('Missing email');
  } else if (!isValidEmail(row.email)) {
    errors.push('Invalid email format');
  }

  if (!isNoAccess) {
    if (!row.total.trim()) {
      errors.push('Missing billing amount');
    } else if (isNaN(parseFloat(row.total.replace(/[,$]/g, '')))) {
      errors.push('Invalid billing amount');
    }
  }

  let status: ValidationStatus = 'READY';

  if (isNoAccess) {
    status = 'NO_ACCESS';
    return { rowIndex: row.rowIndex, isValid: true, errors: [], status };
  }

  if (!isValidEmail(row.email)) {
    status = 'INVALID_EMAIL';
  } else {
    const pdfMatch = findPdfForCompany(row.companyName, pdfIndex);
    if (!pdfMatch) {
      errors.push('PDF not found in ZIP');
      status = 'MISSING_PDF';
    }
  }

  if (errors.length > 0 && status === 'READY') {
    status = 'ERROR';
  }

  return {
    rowIndex: row.rowIndex,
    isValid: errors.length === 0,
    errors,
    status,
  };
}

export function buildProcessedRow(
  row: BillingRow,
  pdfIndex: Map<string, string>,
  selectTemplate: (notes: string) => ProcessedRow['template']
): ProcessedRow {
  const validation = validateRow(row, pdfIndex);
  const pdfMatch = validation.status !== 'NO_ACCESS' && validation.status !== 'INVALID_EMAIL'
    ? findPdfForCompany(row.companyName, pdfIndex)
    : null;

  return {
    ...row,
    pdfFilename: pdfMatch?.filename ?? null,
    pdfPath: pdfMatch?.path ?? null,
    pdfStatus: pdfMatch ? 'FOUND' : 'MISSING',
    template: selectTemplate(row.notes),
    parsedCC: parseEmailList(row.cc),
    parsedBCC: parseEmailList(row.bcc),
    validationStatus: validation.status,
    sendStatus: 'PENDING',
    approved: false,
    dateSent: null,
    emailSent: false,
    processedBy: '',
    errorLog: validation.errors.join('; '),
    hubspotTicketId: row.ticketNumber || null,
  };
}
