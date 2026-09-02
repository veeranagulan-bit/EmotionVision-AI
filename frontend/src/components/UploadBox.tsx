import { useCallback, useRef, useState } from "react";
import { ImageUp, X } from "lucide-react";

const ACCEPTED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
const MAX_SIZE_MB = 8;

interface UploadBoxProps {
  onFileSelected: (file: File) => void;
  previewUrl: string | null;
  onClear: () => void;
  disabled?: boolean;
}

export function UploadBox({ onFileSelected, previewUrl, onClear, disabled }: UploadBoxProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSelect = useCallback(
    (file: File) => {
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setError("Unsupported image format. Please upload JPG, PNG, or WEBP.");
        return;
      }
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setError(`File is too large. Maximum upload size is ${MAX_SIZE_MB}MB.`);
        return;
      }
      setError(null);
      onFileSelected(file);
    },
    [onFileSelected]
  );

  if (previewUrl) {
    return (
      <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)]">
        <img src={previewUrl} alt="Uploaded preview" className="max-h-[420px] w-full object-contain" />
        <button
          onClick={onClear}
          disabled={disabled}
          className="absolute right-3 top-3 flex items-center gap-1.5 rounded-full bg-black/60 px-3 py-1.5 text-xs font-medium text-white backdrop-blur transition-colors hover:bg-black/80 disabled:opacity-50"
        >
          <X size={13} /> Remove Image
        </button>
      </div>
    );
  }

  return (
    <div>
      <label
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          const file = e.dataTransfer.files?.[0];
          if (file) validateAndSelect(file);
        }}
        className={`flex min-h-[280px] cursor-pointer flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors ${
          isDragging
            ? "border-signal-violet bg-signal-violet/5"
            : "border-[var(--border)] bg-[var(--surface)] hover:border-signal-violet/60"
        }`}
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-spectrum-gradient text-white">
          <ImageUp size={26} />
        </span>
        <div>
          <p className="font-display text-base font-semibold text-[var(--text)]">
            Drag &amp; drop your image
          </p>
          <p className="mt-1 text-sm text-[var(--text-muted)]">or click to choose a file</p>
        </div>
        <span className="rounded-full border border-[var(--border)] px-4 py-1.5 text-xs uppercase tracking-wide text-[var(--text-muted)]">
          JPG · PNG · WEBP · up to {MAX_SIZE_MB}MB
        </span>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES.join(",")}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) validateAndSelect(file);
            e.target.value = "";
          }}
        />
      </label>
      {error && <p className="mt-3 text-sm text-signal-coral">{error}</p>}
    </div>
  );
}
