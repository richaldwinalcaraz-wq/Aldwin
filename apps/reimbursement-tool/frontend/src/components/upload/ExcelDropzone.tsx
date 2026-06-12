import { useRef, useState } from 'react';
import { FileSpreadsheet, X, CheckCircle } from 'lucide-react';

interface Props {
  file: File | null;
  onFile: (f: File | null) => void;
  disabled?: boolean;
}

export function ExcelDropzone({ file, onFile, disabled }: Props) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith('.xlsx')) onFile(f);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) onFile(f);
    e.target.value = '';
  }

  return (
    <div
      className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer ${
        dragging
          ? 'border-[#F47920] bg-orange-50'
          : file
          ? 'border-green-400 bg-green-50'
          : 'border-gray-300 hover:border-[#F47920] hover:bg-orange-50/30 bg-white'
      } ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx"
        className="hidden"
        onChange={handleChange}
      />

      {file ? (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900">{file.name}</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {(file.size / 1024).toFixed(0)} KB
              </p>
            </div>
          </div>
          <button
            className="p-1 text-gray-400 hover:text-gray-700 transition-colors"
            onClick={(e) => { e.stopPropagation(); onFile(null); }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div>
          <FileSpreadsheet className="w-8 h-8 text-gray-400 mx-auto mb-3" />
          <p className="text-sm font-medium text-gray-600">
            Drop Excel file here
          </p>
          <p className="text-xs text-gray-400 mt-1">.xlsx only · Billing sheet</p>
        </div>
      )}
    </div>
  );
}
