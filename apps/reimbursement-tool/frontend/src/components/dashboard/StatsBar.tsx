import { ProcessedRow } from '../../types';

interface Props {
  rows: ProcessedRow[];
}

export function StatsBar({ rows }: Props) {
  const total = rows.length;
  const sent = rows.filter((r) => r.sendStatus === 'SENT').length;
  const failed = rows.filter((r) => r.sendStatus === 'FAILED').length;
  const missingPdf = rows.filter((r) => r.pdfStatus === 'MISSING').length;
  const pending = rows.filter((r) => r.sendStatus === 'PENDING').length;
  const noAccess = rows.filter((r) => r.validationStatus === 'NO_ACCESS').length;
  const emailsSent = rows.filter((r) => r.emailSent).length;

  const stats = [
    { label: 'Total Rows', value: total, color: 'text-[#1B3A8A]' },
    { label: 'Sent', value: sent, color: 'text-green-600' },
    { label: 'Failed', value: failed, color: 'text-red-600' },
    { label: 'Missing PDFs', value: missingPdf, color: 'text-amber-600' },
    { label: 'No Access', value: noAccess, color: 'text-gray-500' },
    { label: 'Pending', value: pending, color: 'text-gray-500' },
    { label: 'Emails Sent', value: emailsSent, color: 'text-blue-600' },
  ];

  return (
    <div className="grid grid-cols-7 gap-4">
      {stats.map(({ label, value, color }) => (
        <div key={label} className="card p-4">
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
          <p className="text-xs text-gray-500 mt-1">{label}</p>
        </div>
      ))}
    </div>
  );
}
