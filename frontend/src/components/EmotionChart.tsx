import { motion } from "framer-motion";
import { EMOTION_EMOJI } from "../types";

interface EmotionChartProps {
  probabilities: Record<string, number>;
}

const BAR_COLORS = ["#8B7FFF", "#FF7A59", "#45C4B0", "#F5C56B", "#B7BBC9", "#5A6072", "#20242F"];

export function EmotionChart({ probabilities }: EmotionChartProps) {
  const sorted = Object.entries(probabilities).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-3">
      {sorted.map(([emotion, value], i) => {
        const pct = Math.round(value * 1000) / 10;
        return (
          <div key={emotion}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="flex items-center gap-1.5 text-[var(--text)]">
                <span aria-hidden>{EMOTION_EMOJI[emotion] ?? "🙂"}</span>
                {emotion}
              </span>
              <span className="font-mono text-xs text-[var(--text-muted)]">{pct.toFixed(1)}%</span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--surface-alt)]">
              <motion.div
                className="h-full rounded-full"
                style={{ backgroundColor: BAR_COLORS[i % BAR_COLORS.length] }}
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.7, ease: "easeOut", delay: i * 0.05 }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
