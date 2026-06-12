import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';

dotenv.config();

import uploadRouter from './routes/upload';
import previewRouter from './routes/preview';
import processRouter from './routes/process';
import exportRouter from './routes/export';
import hubspotRouter from './routes/hubspot';
import { cleanupOldSessions } from './store/sessionStore';

const app = express();
const PORT = parseInt(process.env.PORT ?? '3001', 10);

// Ensure required directories exist
const dirs = [
  process.env.UPLOAD_DIR ?? './uploads',
  process.env.EXPORT_DIR ?? './exports',
];
for (const dir of dirs) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

app.use(cors({ origin: 'http://localhost:3000', credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/upload', uploadRouter);
app.use('/api/preview', previewRouter);
app.use('/api/process', processRouter);
app.use('/api/export', exportRouter);
app.use('/api/hubspot', hubspotRouter);

// Health check
app.get('/api/health', (_req, res) => {
  res.json({ ok: true, timestamp: new Date().toISOString() });
});

// Error handler
app.use(
  (
    err: Error,
    _req: express.Request,
    res: express.Response,
    _next: express.NextFunction
  ) => {
    console.error(err.stack);
    res.status(500).json({ error: err.message || 'Internal server error' });
  }
);

// Session cleanup every hour
setInterval(() => cleanupOldSessions(), 60 * 60 * 1000);

app.listen(PORT, () => {
  console.log(`Reimbursement Tool backend running on http://localhost:${PORT}`);
});

export default app;
