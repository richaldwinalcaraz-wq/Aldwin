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
  _raw: Record<string, unknown>;
}

export interface ProcessedRow extends BillingRow {
  pdfFilename: string | null;
  pdfPath: string | null;
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

export interface HubSpotTicket {
  id: string;
  subject: string;
  hs_ticket_priority: string;
  content: string;
}

export interface ValidationResult {
  rowIndex: number;
  isValid: boolean;
  errors: string[];
  status: ValidationStatus;
}

export interface ExportRecord {
  filename: string;
  processedDate: string;
  totalSent: number;
  failedRows: number;
  path: string;
}

export interface Session {
  sessionId: string;
  excelBuffer: Buffer;
  excelFilename: string;
  zipPath: string;
  parsedRows: BillingRow[];
  processedRows: ProcessedRow[];
  pdfIndex: Map<string, string>;
  exportRecords: ExportRecord[];
  processing: boolean;
  createdAt: Date;
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
