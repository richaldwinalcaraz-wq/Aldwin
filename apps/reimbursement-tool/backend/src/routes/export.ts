import { Router, Request, Response } from 'express';
import * as path from 'path';
import * as fs from 'fs';
import { getSession } from '../store/sessionStore';
import { generateWriteBack } from '../services/excelService';

const router = Router();
const EXPORT_DIR = process.env.EXPORT_DIR ?? './exports';

// Generate write-back Excel
router.post('/', (req: Request, res: Response) => {
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

  try {
    const filename = generateWriteBack(
      session.excelBuffer,
      session.processedRows,
      EXPORT_DIR
    );

    const totalSent = session.processedRows.filter((r) => r.sendStatus === 'SENT').length;
    const failedRows = session.processedRows.filter((r) => r.sendStatus === 'FAILED').length;

    const record = {
      filename,
      processedDate: new Date().toLocaleString('en-US', { timeZone: 'Asia/Manila' }),
      totalSent,
      failedRows,
      path: path.join(EXPORT_DIR, filename),
    };

    session.exportRecords.push(record);

    res.json({ filename, totalSent, failedRows });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Export failed';
    res.status(500).json({ error: message });
  }
});

// Download export file
router.get('/:filename', (req: Request, res: Response) => {
  const { filename } = req.params;

  // Sanitize filename — prevent path traversal
  const safeFilename = path.basename(filename);
  const filePath = path.join(EXPORT_DIR, safeFilename);

  if (!fs.existsSync(filePath)) {
    res.status(404).json({ error: 'Export file not found' });
    return;
  }

  res.download(filePath, safeFilename);
});

// List export history for a session
router.get('/', (req: Request, res: Response) => {
  const { sessionId } = req.query;

  if (!sessionId || typeof sessionId !== 'string') {
    res.status(400).json({ error: 'sessionId required' });
    return;
  }

  const session = getSession(sessionId);
  if (!session) {
    res.json({ records: [] });
    return;
  }

  res.json({ records: session.exportRecords });
});

export default router;
