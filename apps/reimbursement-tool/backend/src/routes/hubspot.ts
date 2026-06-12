import { Router, Request, Response } from 'express';
import { testHubSpotConnection } from '../services/hubspotService';
import { getAppSettings, updateAppSettings } from '../store/sessionStore';

const router = Router();

// Test HubSpot connection
router.get('/test', async (req: Request, res: Response) => {
  const token =
    (req.headers['x-hubspot-token'] as string) || getAppSettings().hubspotToken;

  if (!token) {
    res.status(400).json({ ok: false, error: 'No HubSpot token provided' });
    return;
  }

  const result = await testHubSpotConnection(token);
  res.json(result);
});

// Save settings
router.post('/settings', (req: Request, res: Response) => {
  const { hubspotToken, processedBy, templateIds } = req.body;

  updateAppSettings({
    ...(hubspotToken !== undefined && { hubspotToken }),
    ...(processedBy !== undefined && { processedBy }),
    ...(templateIds !== undefined && { templateIds }),
  });

  res.json({ ok: true });
});

// Get current settings (mask sensitive fields)
router.get('/settings', (_req: Request, res: Response) => {
  const settings = getAppSettings();
  res.json({
    hubspotToken: settings.hubspotToken ? '***' + settings.hubspotToken.slice(-4) : '',
    processedBy: settings.processedBy,
    templateIds: settings.templateIds,
    configured: Object.entries(settings.templateIds)
      .some(([k, v]) => k !== 'fromEmail' && typeof v === 'number' && v > 0),
  });
});

export default router;
