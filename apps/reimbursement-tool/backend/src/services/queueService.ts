import { Response } from 'express';
import { ProcessedRow, Session, SSEEvent, AppSettings } from '../types';
import { createOrUpdateTicket, logEmailEngagement } from './hubspotService';
import { sendEmail } from './emailService';

function formatPhilippineTime(): string {
  return new Date().toLocaleString('en-US', {
    timeZone: 'Asia/Manila',
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).replace(',', '');
}

function emitSSE(clients: Map<string, Response>, sessionId: string, event: SSEEvent): void {
  const client = clients.get(sessionId);
  if (client) {
    client.write(`data: ${JSON.stringify(event)}\n\n`);
  }
}

export async function processQueue(
  session: Session,
  settings: AppSettings,
  sseClients: Map<string, Response>
): Promise<void> {
  const approvedRows = session.processedRows.filter(
    (r) => r.approved && r.validationStatus !== 'ERROR'
  );

  const total = approvedRows.length;
  let current = 0;

  session.processing = true;

  for (const row of approvedRows) {
    current++;

    // Update status to PROCESSING
    row.sendStatus = 'PROCESSING';
    row.processedBy = settings.processedBy;
    emitSSE(sseClients, session.sessionId, {
      type: 'row_update',
      rowIndex: row.rowIndex,
      status: 'PROCESSING',
      message: `Processing ${row.companyName}...`,
      current,
      total,
    });

    try {
      // Handle NO_ACCESS rows
      if (row.validationStatus === 'NO_ACCESS') {
        const emailResult = await sendEmail(row, settings.templateIds, settings.hubspotToken);
        if (emailResult.success) {
          row.sendStatus = 'NO_ACCESS';
          row.emailSent = true;
          row.dateSent = formatPhilippineTime();
        } else {
          row.sendStatus = 'FAILED';
          row.errorLog = emailResult.error ?? 'Email send failed';
        }
        emitSSE(sseClients, session.sessionId, {
          type: 'row_update',
          rowIndex: row.rowIndex,
          status: row.sendStatus,
          message: `${row.companyName}: ${row.sendStatus}`,
          current,
          total,
        });
        continue;
      }

      // Skip rows with missing PDF or invalid email
      if (row.validationStatus === 'MISSING_PDF') {
        row.sendStatus = 'FAILED';
        row.errorLog = 'Missing PDF';
        emitSSE(sseClients, session.sessionId, {
          type: 'row_update',
          rowIndex: row.rowIndex,
          status: 'FAILED',
          message: `${row.companyName}: Missing PDF`,
          current,
          total,
        });
        continue;
      }

      if (row.validationStatus === 'INVALID_EMAIL') {
        row.sendStatus = 'FAILED';
        row.errorLog = 'Invalid email';
        emitSSE(sseClients, session.sessionId, {
          type: 'row_update',
          rowIndex: row.rowIndex,
          status: 'FAILED',
          message: `${row.companyName}: Invalid email`,
          current,
          total,
        });
        continue;
      }

      // Step 1: Create/update HubSpot ticket
      let ticketId: string | null = null;
      if (settings.hubspotToken) {
        emitSSE(sseClients, session.sessionId, {
          type: 'progress',
          rowIndex: row.rowIndex,
          message: `Creating ticket for ${row.companyName}...`,
          current,
          total,
        });

        const ticketResult = await createOrUpdateTicket(row, settings.hubspotToken);
        ticketId = ticketResult.ticketId;
        row.hubspotTicketId = ticketId;
      }

      // Step 2: Send email
      emitSSE(sseClients, session.sessionId, {
        type: 'progress',
        rowIndex: row.rowIndex,
        message: `Sending email to ${row.email}...`,
        current,
        total,
      });

      const emailResult = await sendEmail(row, settings.templateIds, settings.hubspotToken);

      if (emailResult.success) {
        row.sendStatus = 'SENT';
        row.emailSent = true;
        row.dateSent = formatPhilippineTime();
        row.errorLog = '';

        // Step 3: Log engagement in HubSpot
        if (settings.hubspotToken && ticketId) {
          await logEmailEngagement(row, ticketId, settings.hubspotToken);
        }
      } else {
        row.sendStatus = 'FAILED';
        row.emailSent = false;
        row.errorLog = emailResult.error ?? 'Email send failed';
      }

      emitSSE(sseClients, session.sessionId, {
        type: 'row_update',
        rowIndex: row.rowIndex,
        status: row.sendStatus,
        message: `${row.companyName}: ${row.sendStatus}`,
        ticketId: ticketId ?? undefined,
        current,
        total,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      row.sendStatus = 'FAILED';
      row.errorLog = message;
      emitSSE(sseClients, session.sessionId, {
        type: 'row_update',
        rowIndex: row.rowIndex,
        status: 'FAILED',
        message: `${row.companyName}: ${message}`,
        current,
        total,
      });
    }
  }

  session.processing = false;

  emitSSE(sseClients, session.sessionId, {
    type: 'complete',
    message: `Processing complete. ${approvedRows.filter((r) => r.sendStatus === 'SENT').length} sent.`,
    current: total,
    total,
  });
}
