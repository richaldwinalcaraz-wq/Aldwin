import { useState } from 'react';
import { AlertCircle, Search } from 'lucide-react';
import { ProcessedRow } from '../../types';

interface Props {
  rows: ProcessedRow[];
}

export function ErrorLog({ rows }: Props) {
  const [search, setSearch] = useState('');

  const errorRows = rows.filter(
    (r) =>
      r.errorLog ||
      r.sendStatus === 'FAILED' ||
      r.validationStatus === 'MISSING_PDF' ||
      r.validationStatus === 'INVALID_EMAIL' ||
      r.validationStatus === 'ERROR'
  );

  const filtered = errorRows.filter((r) => {
    const q = search.toLowerCase();
    return (
      r.companyName.toLowerCase().includes(q) ||
      r.email.toLowerCase().includes(q) ||
      r.errorLog.toLowerCase().includes(q)
    );
  });

  if (errorRows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <AlertCircle className="w-10 h-10 text-gray-300 mb-3" />
        <p className="text-sm text-gray-500">No errors recorded.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative max-w-xs">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
        <input
          className="input pl-8 py-1.5 text-xs"
          placeholder="Filter errors..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-3 text-left text-gray-500 font-medium">Row</th>
              <th className="px-4 py-3 text-left text-gray-500 font-medium">Company</th>
              <th className="px-4 py-3 text-left text-gray-500 font-medium">Email</th>
              <th className="px-4 py-3 text-left text-gray-500 font-medium">Validation</th>
              <th className="px-4 py-3 text-left text-gray-500 font-medium">Send Status</th>
              <th className="px-4 py-3 text-left text-gray-500 font-medium">Error</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map((row) => (
              <tr key={row.rowIndex} className="table-row-hover">
                <td className="px-4 py-3 text-gray-500 font-mono">{row.rowIndex + 1}</td>
                <td className="px-4 py-3 text-gray-900 font-medium">{row.companyName || '—'}</td>
                <td className="px-4 py-3 text-gray-500">{row.email || '—'}</td>
                <td className="px-4 py-3">
                  <span className={row.validationStatus === 'READY' ? 'badge-green' : 'badge-red'}>
                    {row.validationStatus.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={row.sendStatus === 'SENT' ? 'badge-green' : 'badge-red'}>
                    {row.sendStatus}
                  </span>
                </td>
                <td className="px-4 py-3 text-red-600 max-w-xs truncate" title={row.errorLog}>
                  {row.errorLog || '—'}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No matching errors
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
