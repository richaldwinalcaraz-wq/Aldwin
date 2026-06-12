import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import { ProcessedRow, HubSpotTemplateIds } from '../types';
import { buildEmailSubject, buildEmailHtml } from './templateService';

const HUBSPOT_TRANSACTIONAL_URL =
  'https://api.hubapi.com/marketing/v3/transactional/single-email/send';

function getCurrentPeriod(): string {
  const now = new Date();
  return now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}

export async function sendEmail(
  row: ProcessedRow,
  templateIds: HubSpotTemplateIds,
  hubspotToken: string
): Promise<{ success: boolean; error?: string }> {
  const emailId = templateIds[row.template as keyof Omit<HubSpotTemplateIds, 'fromEmail'>];
  if (!emailId) {
    return {
      success: false,
      error: `No HubSpot template ID configured for template type: ${row.template}`,
    };
  }

  const period = getCurrentPeriod();

  const message: Record<string, unknown> = {
    to: row.email,
    sendId: `row-${row.rowIndex}-${Date.now()}`,
    ...(templateIds.fromEmail ? { from: templateIds.fromEmail } : {}),
    ...(row.parsedCC.length > 0 ? { cc: row.parsedCC } : {}),
    ...(row.parsedBCC.length > 0 ? { bcc: row.parsedBCC } : {}),
  };

  // Attach PDF for all templates except informational
  if (row.template !== 'informational' && row.pdfPath && fs.existsSync(row.pdfPath)) {
    const pdfBuffer = fs.readFileSync(row.pdfPath);
    message.attachments = [
      {
        fileName: row.pdfFilename ?? path.basename(row.pdfPath),
        base64Data: pdfBuffer.toString('base64'),
        fileType: 'application/pdf',
        isInline: false,
      },
    ];
  }

  const payload = {
    emailId,
    message,
    customProperties: {
      companyName: row.companyName,
      total: row.total,
      currency: row.currency,
      totalToCharge: row.totalToCharge,
      pastDue: row.pastDue,
      period,
      sentBy: row.processedBy || row.reportSentBy || 'Billing Team',
    },
  };

  try {
    const response = await axios.post(HUBSPOT_TRANSACTIONAL_URL, payload, {
      headers: {
        Authorization: `Bearer ${hubspotToken}`,
        'Content-Type': 'application/json',
      },
    });

    const statusId = response.data?.statusId;
    if (statusId === 'QUEUED' || statusId === 'SENT') {
      return { success: true };
    }
    return { success: false, error: `HubSpot returned status: ${statusId}` };
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      const msg =
        err.response?.data?.message ??
        err.response?.data?.error ??
        err.message;
      return { success: false, error: msg };
    }
    return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
  }
}

export function buildEmailPreview(
  row: ProcessedRow,
  period: string = getCurrentPeriod()
) {
  const subject = buildEmailSubject(row.template, row.companyName, period);
  const html = buildEmailHtml({
    template: row.template,
    companyName: row.companyName,
    total: row.total,
    currency: row.currency,
    totalToCharge: row.totalToCharge,
    pastDue: row.pastDue,
    notes: row.notes,
    sentBy: row.processedBy || row.reportSentBy || 'Billing Team',
    period,
  });

  return {
    rowIndex: row.rowIndex,
    to: row.email,
    cc: row.parsedCC,
    bcc: row.parsedBCC,
    subject,
    templateType: row.template,
    bodyHtml: html,
    pdfFilename: row.pdfFilename,
    hasPdf: row.template !== 'informational' && !!row.pdfPath,
  };
}
