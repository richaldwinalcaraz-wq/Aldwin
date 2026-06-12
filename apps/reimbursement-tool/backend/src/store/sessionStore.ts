import { Session } from '../types';

const sessions = new Map<string, Session>();

export function getSession(sessionId: string): Session | undefined {
  return sessions.get(sessionId);
}

export function setSession(session: Session): void {
  sessions.set(session.sessionId, session);
}

export function deleteSession(sessionId: string): void {
  sessions.delete(sessionId);
}

export function cleanupOldSessions(maxAgeMs = 4 * 60 * 60 * 1000): void {
  const cutoff = new Date(Date.now() - maxAgeMs);
  for (const [id, session] of sessions.entries()) {
    if (session.createdAt < cutoff) {
      sessions.delete(id);
    }
  }
}

// In-memory app settings (configurable via UI)
let appSettings = {
  hubspotToken: process.env.HUBSPOT_ACCESS_TOKEN ?? '',
  processedBy: '',
  templateIds: {
    standard: '' as number | '',
    informational: '' as number | '',
    follow_up: '' as number | '',
    resubmission: '' as number | '',
    priority: '' as number | '',
    fromEmail: '',
  },
};

export function getAppSettings() {
  return { ...appSettings };
}

export function updateAppSettings(partial: Partial<typeof appSettings>): void {
  appSettings = { ...appSettings, ...partial };
}

// SSE client registry (sessionId → Response)
import { Response } from 'express';
const sseClients = new Map<string, Response>();

export function getSseClients(): Map<string, Response> {
  return sseClients;
}
