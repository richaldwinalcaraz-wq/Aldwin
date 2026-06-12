import multer from 'multer';
import * as path from 'path';
import * as fs from 'fs';

const MAX_MB = parseInt(process.env.MAX_FILE_SIZE_MB ?? '50', 10);
const UPLOAD_DIR = process.env.UPLOAD_DIR ?? './uploads';

if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname);
    const base = path.basename(file.originalname, ext).replace(/[^a-zA-Z0-9_-]/g, '_');
    const timestamp = Date.now();
    cb(null, `${base}_${timestamp}${ext}`);
  },
});

function fileFilter(
  _req: Express.Request,
  file: Express.Multer.File,
  cb: multer.FileFilterCallback
): void {
  const ext = path.extname(file.originalname).toLowerCase();
  const mime = file.mimetype;

  const allowed =
    (ext === '.xlsx' &&
      (mime === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        mime === 'application/octet-stream')) ||
    (ext === '.zip' && (mime === 'application/zip' || mime === 'application/x-zip-compressed' || mime === 'application/octet-stream'));

  if (allowed) {
    cb(null, true);
  } else {
    cb(new Error(`Invalid file type: ${ext}. Only .xlsx and .zip allowed.`));
  }
}

export const uploadMiddleware = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: MAX_MB * 1024 * 1024,
  },
});
