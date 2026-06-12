import { useState } from 'react';
import { Eye, ChevronUp, ChevronDown, Search } from 'lucide-react';
import { ProcessedRow, ValidationStatus, SendStatus, EmailTemplateType } from '../../types';
import { useProcessingStore } from '../../store/processingStore';

interface Props {
  rows: ProcessedRow[];
  onPreview: (row: ProcessedRow) => void;
  onToggleApprove: (rowIndex: number, approved: boolean) => void;
}

const STATUS_BADGE: Record<ValidationStatus | SendStatus, string> = {
  READY: 'badge-green',
  MISSING_PDF: 'badge-red',
  INVALID_EMAIL: 'badge-red',
  NO_ACCESS: 'badge-yellow',
  ERROR: 'badge-red',
  PENDING: 'badge-gray',
  PROCESSING: 'badge-blue',
  SENT: 'badge-green',
  FAILED: 'badge-red',
  SKIPPED: 'badge-gray',
};

const TEMPLATE_LABELS: Record<EmailTemplateType, string> = {
  standard: 'Standard',
  informational: 'Info (No Access)',
  follow_up: 'Follow-Up',
  resubmission: 'Resubmission',
  priority: 'Priority',
};

type SortKey = 'companyName' | 'validationStatus' | 'sendStatus' | 'template';

export function ProcessingTable({ rows, onPreview, onToggleApprove }: Props) {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortKey, setSortKey] = useState<SortKey>('companyName');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(0);
  const perPage = 25;

  const { rowStatuses } = useProcessingStore();

  // Merge live processing statuses
  const enrichedRows = rows.map((r) => {
    const live = rowStatuses.get(r.rowIndex);
    if (live) return { ...r, sendStatus: live.sendStatus };
    return r;
  });

  const filtered = enrichedRows
    .filter((r) => {
      const q = search.toLowerCase();
      return (
        r.companyName.toLowerCase().includes(q) ||
        r.email.toLowerCase().includes(q)
      );
    })
    .filter((r) =>
      statusFilter === 'all' ? true : r.validationStatus === statusFilter || r.sendStatus === statusFilter
    )
    .sort((a, b) => {
      const av = String(a[sortKey] ?? '');
      const bv = String(b[sortKey] ?? '');
      return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
    });

  const totalPages = Math.ceil(filtered.length / perPage);
  const pageRows = filtered.slice(page * perPage, (page + 1) * perPage);

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortKey(key); setSortDir('asc'); }
  }

  function SortIcon({ k }: { k: SortKey }) {
    if (sortKey !== k) return null;
    return sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />;
  }

  return (
    <div className="card overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center gap-3 p-4 border-b border-gray-200">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            className="input pl-8 py-1.5 text-xs"
            placeholder="Search company or email..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          />
        </div>

        <select
          className="input py-1.5 text-xs max-w-[160px]"
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
        >
          <option value="all">All Status</option>
          <option value="READY">Ready</option>
          <option value="MISSING_PDF">Missing PDF</option>
          <option value="INVALID_EMAIL">Invalid Email</option>
          <option value="NO_ACCESS">No Access</option>
          <option value="SENT">Sent</option>
          <option value="FAILED">Failed</option>
        </select>

        <span className="text-xs text-gray-500 ml-auto">
          {filtered.length} rows
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  className="rounded"
                  onChange={(e) => {
                    pageRows.forEach((r) => {
                      if (r.validationStatus === 'READY' || r.validationStatus === 'NO_ACCESS') {
                        onToggleApprove(r.rowIndex, e.target.checked);
                      }
                    });
                  }}
                />
              </th>
              {[
                { label: 'Company', key: 'companyName' as SortKey },
                { label: 'Email', key: null },
                { label: 'Ticket', key: null },
                { label: 'PDF', key: null },
                { label: 'Template', key: 'template' as SortKey },
                { label: 'Validation', key: 'validationStatus' as SortKey },
                { label: 'Status', key: 'sendStatus' as SortKey },
                { label: '', key: null },
              ].map(({ label, key }) => (
                <th
                  key={label}
                  className={`px-4 py-3 text-left text-gray-500 font-medium ${
                    key ? 'cursor-pointer hover:text-[#1B3A8A] select-none' : ''
                  }`}
                  onClick={() => key && toggleSort(key)}
                >
                  <span className="flex items-center gap-1">
                    {label}
                    {key && <SortIcon k={key} />}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {pageRows.map((row) => (
              <tr key={row.rowIndex} className="table-row-hover">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={row.approved}
                    disabled={row.validationStatus === 'MISSING_PDF' || row.validationStatus === 'INVALID_EMAIL' || row.validationStatus === 'ERROR'}
                    onChange={(e) => onToggleApprove(row.rowIndex, e.target.checked)}
                    className="rounded"
                  />
                </td>
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-900 truncate max-w-[180px]">{row.companyName || '—'}</p>
                </td>
                <td className="px-4 py-3 text-gray-500 truncate max-w-[160px]">{row.email || '—'}</td>
                <td className="px-4 py-3 text-gray-400 font-mono">
                  {row.hubspotTicketId || <span className="text-gray-300">—</span>}
                </td>
                <td className="px-4 py-3">
                  <span className={row.pdfStatus === 'FOUND' ? 'badge-green' : 'badge-red'}>
                    {row.pdfStatus === 'FOUND' ? row.pdfFilename ?? 'Found' : 'Missing'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-gray-700">
                    {TEMPLATE_LABELS[row.template]}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={STATUS_BADGE[row.validationStatus]}>
                    {row.validationStatus.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={STATUS_BADGE[row.sendStatus]}>
                    {row.sendStatus}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    className="btn-ghost p-1"
                    onClick={() => onPreview(row)}
                    title="Preview email"
                  >
                    <Eye className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
            {pageRows.length === 0 && (
              <tr>
                <td colSpan={9} className="px-4 py-8 text-center text-gray-500">
                  No rows match filters
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
          <span className="text-xs text-gray-500">
            Page {page + 1} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              className="btn-ghost px-3 py-1 text-xs"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <button
              className="btn-ghost px-3 py-1 text-xs"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
