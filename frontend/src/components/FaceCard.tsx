import { EMOTION_EMOJI, type FacePrediction } from "../types";

interface FaceCardProps {
  prediction: FacePrediction;
  isSelected: boolean;
  onSelect: () => void;
}

export function FaceCard({ prediction, isSelected, onSelect }: FaceCardProps) {
  const pct = Math.round(prediction.confidence * 100);

  return (
    <button
      onClick={onSelect}
      className={`w-full rounded-xl border px-4 py-3 text-left transition-colors ${
        isSelected
          ? "border-signal-violet bg-signal-violet/10"
          : "border-[var(--border)] bg-[var(--surface)] hover:border-signal-violet/50"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-[var(--text)]">Face {prediction.face_id}</span>
        <span className="font-mono text-xs text-[var(--text-muted)]">{pct}%</span>
      </div>
      <div className="mt-1 flex items-center gap-2">
        <span aria-hidden>{EMOTION_EMOJI[prediction.emotion] ?? "🙂"}</span>
        <span className="text-sm text-[var(--text-muted)]">
          {prediction.is_uncertain ? "Uncertain" : prediction.emotion}
        </span>
      </div>
    </button>
  );
}
