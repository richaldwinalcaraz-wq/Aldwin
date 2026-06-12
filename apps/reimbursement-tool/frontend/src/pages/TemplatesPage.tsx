const TEMPLATES = [
  {
    key: 'standard',
    label: 'Standard',
    trigger: 'Default (any NOTES value)',
    color: 'bg-white border-gray-200',
    dot: 'bg-gray-400',
    description: 'Standard reimbursement report delivery. Attaches PDF. Creates HubSpot ticket.',
    attachPdf: true,
    createTicket: true,
  },
  {
    key: 'informational',
    label: 'Informational (No Access)',
    trigger: 'NOTES = "No Access"',
    color: 'bg-amber-50 border-amber-200',
    dot: 'bg-amber-400',
    description: 'Informs client of no system access for the period. No PDF attached. No ticket created.',
    attachPdf: false,
    createTicket: false,
  },
  {
    key: 'follow_up',
    label: 'Follow-Up (Past Due)',
    trigger: 'NOTES = "Past Due"',
    color: 'bg-red-50 border-red-200',
    dot: 'bg-red-500',
    description: 'Past due balance follow-up. Highlights overdue amount. Attaches PDF. Creates ticket.',
    attachPdf: true,
    createTicket: true,
  },
  {
    key: 'resubmission',
    label: 'Resubmission',
    trigger: 'NOTES = "Resubmission"',
    color: 'bg-orange-50 border-orange-200',
    dot: 'bg-orange-500',
    description: 'Requests client to resubmit or acknowledge updated billing. Attaches PDF. Creates ticket.',
    attachPdf: true,
    createTicket: true,
  },
  {
    key: 'priority',
    label: 'Priority (Urgent)',
    trigger: 'NOTES = "Urgent"',
    color: 'bg-red-50 border-red-300',
    dot: 'bg-red-600',
    description: 'Urgent billing notice requiring immediate action. Attaches PDF. Creates HIGH priority ticket.',
    attachPdf: true,
    createTicket: true,
  },
];

export function TemplatesPage() {
  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#1B3A8A]">Email Templates</h1>
        <p className="text-gray-500 text-sm mt-1">
          Templates are auto-selected based on the NOTES column in your Excel sheet.
        </p>
      </div>

      <div className="space-y-3 max-w-3xl">
        {TEMPLATES.map((t) => (
          <div key={t.key} className={`border rounded-lg p-5 ${t.color}`}>
            <div className="flex items-start gap-4">
              <div className={`w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0 ${t.dot}`} />
              <div className="flex-1">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-sm font-semibold text-gray-900">{t.label}</h3>
                  <code className="text-[11px] text-gray-500 bg-white px-2 py-0.5 rounded border border-gray-200">
                    {t.trigger}
                  </code>
                </div>
                <p className="text-xs text-gray-500 mt-1.5">{t.description}</p>
                <div className="flex gap-4 mt-3">
                  <span className={`text-[11px] ${t.attachPdf ? 'text-green-600' : 'text-gray-400'}`}>
                    {t.attachPdf ? '✓ PDF attached' : '✗ No PDF'}
                  </span>
                  <span className={`text-[11px] ${t.createTicket ? 'text-green-600' : 'text-gray-400'}`}>
                    {t.createTicket ? '✓ HubSpot ticket' : '✗ No ticket'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 p-5 border border-gray-200 bg-white rounded-lg max-w-3xl">
        <h3 className="text-sm font-semibold text-[#1B3A8A] mb-3">Template Selection Logic</h3>
        <div className="font-mono text-xs text-gray-600 space-y-1">
          <p><span className="text-gray-400">if</span> NOTES == <span className="text-amber-600">"No Access"</span>    → <span className="text-gray-700">informational</span></p>
          <p><span className="text-gray-400">if</span> NOTES == <span className="text-red-600">"Past Due"</span>      → <span className="text-gray-700">follow_up</span></p>
          <p><span className="text-gray-400">if</span> NOTES == <span className="text-orange-600">"Resubmission"</span> → <span className="text-gray-700">resubmission</span></p>
          <p><span className="text-gray-400">if</span> NOTES == <span className="text-red-700">"Urgent"</span>        → <span className="text-gray-700">priority</span></p>
          <p><span className="text-gray-400">else</span>                              → <span className="text-gray-700">standard</span></p>
        </div>
        <p className="text-[11px] text-gray-400 mt-3">Case-insensitive. Exact match only.</p>
      </div>
    </div>
  );
}
