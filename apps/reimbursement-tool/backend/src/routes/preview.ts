import { Router, Request, Response } from 'express';
import { getSession } from '../store/sessionStore';
import { buildEmailPreview } from '../services/emailService';

const router = Router();

router.get('/', (req: Request, res: Response) => {
  const { sessionId } = req.query;
  if (!sessionId || typeof sessionId !== 'string') {
    res.status(400).json({ error: 'sessionId required' });
    return;
  }

  const session = getSession(sessionId);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  const rows = session.processedRows.map((r) => {
    const { _raw, pdfPath, ...safe } = r as typeof r & { pdfPath?: string };
    void _raw;
    void pdfPath;
    return safe;
  });

  res.json({ rows });
});

router.post('/email/:rowIndex', (req: Request, res: Response) => {
  const { sessionId } = req.query;
  const rowIndex = parseInt(req.params.rowIndex, 10);

  if (!sessionId || typeof sessionId !== 'string') {
    res.status(400).json({ error: 'sessionId required' });
    return;
  }

  const session = getSession(sessionId);
  if (!session) {
    res.status(404).json({ error: 'Session not found' });
    return;
  }

  const row = session.processedRows.find((r) => r.rowIndex === rowIndex);
  if (!row) {
    res.status(404).json({ error: 'Row not found' });
    return;
  }

  const preview = buildEmailPreview(row);
  res.json(preview);
});

export default router;
