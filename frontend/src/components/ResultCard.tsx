import { motion } from "framer-motion";
import { EMOTION_EMOJI, type FacePrediction } from "../types";
import { EmotionChart } from "./EmotionChart";

interface ResultCardProps {
  prediction: FacePrediction;
  label?: string;
}

export function ResultCard({ prediction, label }: ResultCardProps) {
  const pct = Math.round(prediction.confidence * 1000) / 10;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6"
    >
      <p className="text-xs uppercase tracking-wide text-[var(--text-muted)]">
        {label ?? "Primary expression"}
      </p>

      {prediction.is_uncertain ? (
        <div className="mt-3">
          <p className="font-display text-2xl font-semibold text-signal-amber">Uncertain</p>
          <p className="mt-1 text-sm text-[var(--text-muted)]">
            The model has low confidence in this facial-expression classification
            ({pct.toFixed(1)}%). Try a clearer, more front-facing photo.
          </p>
        </div>
      ) : (
        <div className="mt-3 flex items-center gap-4">
          <span className="text-5xl" aria-hidden>
            {EMOTION_EMOJI[prediction.emotion] ?? "🙂"}
          </span>
          <div>
            <p className="font-display text-2xl font-semibold uppercase tracking-tight text-[var(--text)]">
              {prediction.emotion}
            </p>
            <p className="font-mono text-sm text-signal-violet">{pct.toFixed(1)}% confidence</p>
          </div>
        </div>
      )}

      <div className="mt-6 h-2 w-full overflow-hidden rounded-full bg-[var(--surface-alt)]">
        <div
          className="h-full rounded-full bg-spectrum-gradient transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>

      <p className="mt-5 text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
        Emotion distribution
      </p>
      <div className="mt-3">
        <EmotionChart probabilities={prediction.probabilities} />
      </div>
    </motion.div>
  );
}
