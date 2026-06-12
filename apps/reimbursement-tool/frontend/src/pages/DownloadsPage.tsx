import { DownloadCenter } from '../components/downloads/DownloadCenter';

export function DownloadsPage() {
  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#1B3A8A]">Downloads</h1>
        <p className="text-gray-500 text-sm mt-1">
          Generate and download write-back Excel reports.
        </p>
      </div>
      <DownloadCenter />
    </div>
  );
}
