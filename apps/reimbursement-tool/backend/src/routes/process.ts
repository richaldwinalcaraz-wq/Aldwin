import { Router, Request, Response } from 'express';
import { getSession, getAppSettings, getSseClients } from '../store/sessionStore';
import { processQueue } from '../services/queueService';

const router = Router();

// Approve rows for sending
router.post('/approve', (req: Request, res: Response) => {
  const { sessionId, rowIndexes, approveAll } = req.body as {
    sessionId: string;
    rowIndexes?: number[];
    approveAll?: boolean;
  };

  if (!sessionId) {
    res.status(400).json({ error: 'sessionId required' });
    return;
  }

  const session = getSession(sessionId);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  if (approveAll) {
    for (const row of session.processedRows) {
      if (row.validationStatus === 'READY' || row.validationStatus === 'NO_ACCESS') {
        row.approved = true;
      }
    }
  } else if (rowIndexes && Array.isArray(rowIndexes)) {
    for (const idx of rowIndexes) {
      const row = session.processedRows.find((r) => r.rowIndex === idx);
      if (row) row.approved = true;
    }
  }

  res.json({ ok: true });
});

// Unapprove rows
router.post('/unapprove', (req: Request, res: Response) => {
  const { sessionId, rowIndexes } = req.body as {
    sessionId: string;
    rowIndexes: number[];
  };

  const session = getSession(sessionId);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  for (const idx of rowIndexes) {
    const row = session.processedRows.find((r) => r.rowIndex === idx);
    if (row) row.approved = false;
  }

  res.json({ ok: true });
});

// Start bulk send
router.post('/send', async (req: Request, res: Response) => {
  const { sessionId } = req.body as { sessionId: string };

  if (!sessionId) {
    res.status(400).json({ error: 'sessionId required' });
    return;
  }

  const session = getSession(sessionId);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  if (session.processing) {
    res.status(409).json({ error: 'Processing already in progress' });
    return;
  }

  const approved = session.processedRows.filter((r) => r.approved);
  if (approved.length === 0) {
    res.status(400).json({ error: 'No rows approved for sending' });
    return;
  }

  const settings = getAppSettings();
  const anyTemplateConfigured = Object.entries(settings.templateIds)
    .some(([k, v]) => k !== 'fromEmail' && typeof v === 'number' && v > 0);
  if (!anyTemplateConfigured) {
    res.status(400).json({ error: 'No HubSpot template IDs configured. Go to Settings.' });
    return;
  }

  // Fire off queue processing async — SSE handles progress
  processQueue(session, settings, getSseClients()).catch(console.error);

  res.json({ ok: true, queued: approved.length });
});

// SSE stream for real-time progress
router.get('/status', (req: Request, res: Response) => {
  const { sessionId } = req.query;

  if (!sessionId || typeof sessionId !== 'string') {
    res.status(400).json({ error: 'sessionId required' });
    return;
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.flushHeaders();

  // Register SSE client
  getSseClients().set(sessionId, res);

  // Heartbeat to keep connection alive
  const heartbeat = setInterval(() => {
    res.write(': heartbeat\n\n');
  }, 15000);

  req.on('close', () => {
    clearInterval(heartbeat);
    getSseClients().delete(sessionId);
  });
});

export default router;
