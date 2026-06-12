import { Router, Request, Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { uploadMiddleware } from '../middleware/upload';
import { parseExcel } from '../services/excelService';
import { extractZipAndIndex, validateZip } from '../services/zipService';
import { buildProcessedRow } from '../services/validationService';
import { selectTemplate } from '../services/templateService';
import { setSession } from '../store/sessionStore';
import { Session } from '../types';

const router = Router();
const UPLOAD_DIR = process.env.UPLOAD_DIR ?? './uploads';

router.post(
  '/',
  uploadMiddleware.fields([
    { name: 'excel', maxCount: 1 },
    { name: 'zip', maxCount: 1 },
  ]),
  async (req: Request, res: Response) => {
    try {
      const files = req.files as Record<string, Express.Multer.File[]>;

      if (!files?.excel?.[0]) {
        res.status(400).json({ error: 'Excel file required' });
        return;
      }
      if (!files?.zip?.[0]) {
        res.status(400).json({ error: 'ZIP file required' });
        return;
      }

      const excelFile = files.excel[0];
      const zipFile = files.zip[0];

      // Validate ZIP
      const zipValidation = validateZip(zipFile.path);
      if (!zipValidation.valid) {
        res.status(400).json({ error: zipValidation.error });
        return;
      }

      // Read Excel buffer
      const excelBuffer = fs.readFileSync(excelFile.path);

      // Parse Excel
      const billingRows = parseExcel(excelBuffer);
      if (billingRows.length === 0) {
        res.status(400).json({ error: 'Excel file contains no data rows' });
        return;
      }

      // Extract ZIP + build PDF index
      const sessionId = uuidv4();
      const extractDir = path.join(UPLOAD_DIR, sessionId, 'pdfs');
      const pdfIndex = extractZipAndIndex(zipFile.path, extractDir);

      // Build processed rows
      const processedRows = billingRows.map((row) =>
        buildProcessedRow(row, pdfIndex, selectTemplate)
      );

      // Store session
      const session: Session = {
        sessionId,
        excelBuffer,
        excelFilename: excelFile.originalname,
        zipPath: zipFile.path,
        parsedRows: billingRows,
        processedRows,
        pdfIndex,
        exportRecords: [],
        processing: false,
        createdAt: new Date(),
      };
      setSession(session);

      // Summary stats
      const summary = {
        sessionId,
        totalRows: processedRows.length,
        validRows: processedRows.filter((r) => r.validationStatus === 'READY').length,
        missingPdfs: processedRows.filter((r) => r.validationStatus === 'MISSING_PDF').length,
        invalidEmails: processedRows.filter((r) => r.validationStatus === 'INVALID_EMAIL').length,
        noAccessRows: processedRows.filter((r) => r.validationStatus === 'NO_ACCESS').length,
        rows: processedRows.map((r) => {
          const { _raw, pdfPath, ...safe } = r as typeof r & { pdfPath?: string };
          void _raw;
          void pdfPath;
          return safe;
        }),
      };

      res.json(summary);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload processing failed';
      res.status(500).json({ error: message });
    }
  }
);

export default router;
