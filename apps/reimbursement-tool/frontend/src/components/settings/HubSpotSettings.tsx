import { useState } from 'react';
import { CheckCircle, XCircle, Loader2, Eye, EyeOff } from 'lucide-react';
import { api } from '../../lib/api';
import { useSettingsStore } from '../../store/settingsStore';

const TEMPLATE_FIELDS = [
  { key: 'standard', label: 'Standard', dot: 'bg-gray-400' },
  { key: 'informational', label: 'Informational (No Access)', dot: 'bg-amber-400' },
  { key: 'follow_up', label: 'Follow-Up (Past Due)', dot: 'bg-red-500' },
  { key: 'resubmission', label: 'Resubmission', dot: 'bg-orange-500' },
  { key: 'priority', label: 'Priority (Urgent)', dot: 'bg-red-600' },
] as const;

export function HubSpotSettings() {
  const { hubspotToken, processedBy, templateIds, setHubspotToken, setProcessedBy, setTemplateIds } =
    useSettingsStore();

  const [showToken, setShowToken] = useState(false);
  const [testingHub, setTestingHub] = useState(false);
  const [hubStatus, setHubStatus] = useState<'ok' | 'fail' | null>(null);
  const [hubError, setHubError] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function testHubSpot() {
    setTestingHub(true);
    setHubStatus(null);
    try {
      const res = await api.get<{ ok: boolean; error?: string }>('/hubspot/test', {
        headers: { 'x-hubspot-token': hubspotToken },
      });
      setHubStatus(res.data.ok ? 'ok' : 'fail');
      setHubError(res.data.error ?? '');
    } catch (err: unknown) {
      setHubStatus('fail');
      setHubError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setTestingHub(false);
    }
  }

  async function saveSettings() {
    setSaving(true);
    try {
      await api.post('/hubspot/settings', { hubspotToken, processedBy, templateIds });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-8 max-w-2xl">
      {/* Operator info */}
      <section className="card p-5">
        <h3 className="text-sm font-semibold text-[#1B3A8A] mb-4">Operator</h3>
        <div>
          <label className="block text-xs text-gray-500 mb-1.5">Processed By (your name)</label>
          <input
            className="input"
            placeholder="e.g. Daisy"
            value={processedBy}
            onChange={(e) => setProcessedBy(e.target.value)}
          />
          <p className="text-[11px] text-gray-400 mt-1.5">
            Written to PROCESSED BY column in Excel export.
          </p>
        </div>
      </section>

      {/* HubSpot */}
      <section className="card p-5">
        <h3 className="text-sm font-semibold text-[#1B3A8A] mb-4">HubSpot Integration</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1.5">Private App Token</label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  className="input pr-9"
                  type={showToken ? 'text' : 'password'}
                  placeholder="pat-na1-..."
                  value={hubspotToken}
                  onChange={(e) => setHubspotToken(e.target.value)}
                />
                <button
                  type="button"
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
                  onClick={() => setShowToken((v) => !v)}
                >
                  {showToken ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
              <button
                className="btn-secondary text-xs px-3 whitespace-nowrap"
                onClick={testHubSpot}
                disabled={!hubspotToken || testingHub}
              >
                {testingHub ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Test'}
              </button>
            </div>
            {hubStatus && (
              <div className={`flex items-center gap-1.5 mt-1.5 text-xs ${hubStatus === 'ok' ? 'text-green-600' : 'text-red-600'}`}>
                {hubStatus === 'ok' ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                {hubStatus === 'ok' ? 'Connected' : hubError || 'Connection failed'}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* HubSpot Email Templates */}
      <section className="card p-5">
        <h3 className="text-sm font-semibold text-[#1B3A8A] mb-1">HubSpot Email Templates</h3>
        <p className="text-xs text-gray-500 mb-4">
          Emails are sent via HubSpot Transactional Email API using your pre-built templates.
          Find IDs in HubSpot → Marketing → Email → open template → copy numeric ID from URL.
        </p>
        <div className="space-y-3">
          {TEMPLATE_FIELDS.map(({ key, label, dot }) => (
            <div key={key} className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
              <label className="text-xs text-gray-600 w-44 flex-shrink-0">{label}</label>
              <input
                className="input flex-1"
                type="number"
                placeholder="Template ID"
                value={templateIds[key as keyof typeof templateIds] ?? ''}
                onChange={(e) => {
                  const val = e.target.value;
                  setTemplateIds({ [key]: val === '' ? '' : parseInt(val, 10) });
                }}
              />
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100">
          <label className="block text-xs text-gray-500 mb-1.5">
            From Email Address <span className="text-gray-400">(optional — uses template default if blank)</span>
          </label>
          <input
            className="input"
            type="email"
            placeholder="billing@company.com"
            value={templateIds.fromEmail}
            onChange={(e) => setTemplateIds({ fromEmail: e.target.value })}
          />
        </div>
      </section>

      {/* Save */}
      <button className="btn-primary w-full" onClick={saveSettings} disabled={saving}>
        {saving ? (
          <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</>
        ) : saved ? (
          <><CheckCircle className="w-4 h-4" /> Saved</>
        ) : (
          'Save Settings'
        )}
      </button>
    </div>
  );
}
