export type EmailTemplateType = 'standard' | 'informational' | 'follow_up' | 'resubmission' | 'priority';

export type PdfStatus = 'FOUND' | 'MISSING';

export type ValidationStatus = 'READY' | 'MISSING_PDF' | 'INVALID_EMAIL' | 'NO_ACCESS' | 'ERROR';

export type SendStatus = 'PENDING' | 'PROCESSING' | 'SENT' | 'FAILED' | 'SKIPPED' | 'NO_ACCESS';

export interface BillingRow {
  rowIndex: number;
  companyName: string;
  email: string;
  ticketNumber: string;
  notes: string;
  cc: string;
  bcc: string;
  rate: string;
  currency: string;
  total: string;
  convertedUsd: string;
  totalToCharge: string;
  toCarryOver: string;
  btm: string;
  pastDue: string;
  reportSentBy: string;
}

export interface ProcessedRow extends BillingRow {
  pdfFilename: string | null;
  pdfStatus: PdfStatus;
  template: EmailTemplateType;
  parsedCC: string[];
  parsedBCC: string[];
  validationStatus: ValidationStatus;
  sendStatus: SendStatus;
  approved: boolean;
  dateSent: string | null;
  emailSent: boolean;
  processedBy: string;
  errorLog: string;
  hubspotTicketId: string | null;
}

export interface ExportRecord {
  filename: string;
  processedDate: string;
  totalSent: number;
  failedRows: number;
}

export interface EmailPreview {
  rowIndex: number;
  to: string;
  cc: string[];
  bcc: string[];
  subject: string;
  templateType: EmailTemplateType;
  templateLabel: string;
  bodyHtml: string;
  pdfFilename: string | null;
  hasPdf: boolean;
}

export interface HubSpotTemplateIds {
  standard: number | '';
  informational: number | '';
  follow_up: number | '';
  resubmission: number | '';
  priority: number | '';
  fromEmail: string;
}

export interface AppSettings {
  hubspotToken: string;
  processedBy: string;
  templateIds: HubSpotTemplateIds;
}

export interface UploadResponse {
  sessionId: string;
  totalRows: number;
  validRows: number;
  missingPdfs: number;
  invalidEmails: number;
  noAccessRows: number;
  rows: ProcessedRow[];
}

export interface SSEEvent {
  type: 'progress' | 'row_update' | 'complete' | 'error';
  rowIndex?: number;
  status?: SendStatus;
  message?: string;
  ticketId?: string;
  exportFilename?: string;
  total?: number;
  current?: number;
}
