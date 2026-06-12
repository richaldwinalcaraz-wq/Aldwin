import axios, { AxiosInstance } from 'axios';
import { ProcessedRow, HubSpotTicket } from '../types';

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getCurrentPeriod(): string {
  const now = new Date();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const yyyy = now.getFullYear();
  return `${mm}/${yyyy}`;
}

function createClient(token: string): AxiosInstance {
  return axios.create({
    baseURL: 'https://api.hubapi.com',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    timeout: 15000,
  });
}

export async function testHubSpotConnection(token: string): Promise<{ ok: boolean; error?: string }> {
  try {
    const client = createClient(token);
    await client.get('/crm/v3/objects/tickets?limit=1');
    return { ok: true };
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      if (err.response?.status === 401) return { ok: false, error: 'Invalid API token' };
      if (err.response?.status === 403) return { ok: false, error: 'Insufficient permissions' };
      return { ok: false, error: err.message };
    }
    return { ok: false, error: 'Connection failed' };
  }
}

export async function createOrUpdateTicket(
  row: ProcessedRow,
  token: string,
  retries = 2
): Promise<{ ticketId: string; created: boolean }> {
  const client = createClient(token);
  const period = getCurrentPeriod();
  const subject = `[Reimbursement] ${row.companyName} - ${period}`;

  const properties: Record<string, string> = {
    subject,
    content: row.notes || 'Reimbursement report delivery',
    hs_ticket_priority: row.notes.toLowerCase() === 'urgent' ? 'HIGH' : 'MEDIUM',
    hs_pipeline: '0',
    hs_pipeline_stage: '1',
  };

  // Update existing ticket
  if (row.ticketNumber && row.ticketNumber.trim()) {
    try {
      await delay(100);
      const res = await client.patch(`/crm/v3/objects/tickets/${row.ticketNumber}`, {
        properties,
      });
      return { ticketId: String(res.data.id), created: false };
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        // Ticket not found, fall through to create
      } else {
        throw err;
      }
    }
  }

  // Create new ticket
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      await delay(100);
      const res = await client.post('/crm/v3/objects/tickets', { properties });
      return { ticketId: String(res.data.id), created: true };
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 429 && attempt < retries) {
        await delay(1000 * (attempt + 1));
        continue;
      }
      throw err;
    }
  }

  throw new Error('Failed to create HubSpot ticket after retries');
}

export async function logEmailEngagement(
  row: ProcessedRow,
  ticketId: string,
  token: string
): Promise<void> {
  const client = createClient(token);

  const engagement = {
    engagement: {
      active: true,
      type: 'EMAIL',
      timestamp: Date.now(),
    },
    associations: {
      dealIds: [],
      ownerIds: [],
      contactIds: [],
      companyIds: [],
      ticketIds: [parseInt(ticketId, 10)],
    },
    metadata: {
      from: {
        raw: row.reportSentBy || 'Billing Team',
      },
      to: [{ raw: row.email }],
      cc: row.parsedCC.map((e) => ({ raw: e })),
      bcc: row.parsedBCC.map((e) => ({ raw: e })),
      subject: `[Reimbursement] ${row.companyName}`,
      html: `<p>Reimbursement report sent to ${row.email}</p>`,
    },
  };

  try {
    await client.post('/engagements/v1/engagements', engagement);
  } catch {
    // Log failure silently — ticket was created, email engagement log is non-critical
  }
}
