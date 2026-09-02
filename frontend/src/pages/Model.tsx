import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { ApiError, getModelInfo } from "../services/api";
import type { ModelMetrics } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const ARCHITECTURE_FACTS = [
  { label: "Model architecture", value: "Transfer-learning CNN" },
  { label: "Input size", value: "224 × 224" },
  { label: "Framework", value: "TensorFlow / Keras" },
  { label: "Dataset", value: "FER-2013 (or equivalent Kaggle set)" },
  { label: "Task", value: "Facial expression classification" },
];

export function Model() {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [notTrained, setNotTrained] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getModelInfo()
      .then(setMetrics)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setNotTrained(true);
        } else {
          setError("Couldn't reach the backend to load model metrics.");
        }
      });
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-5 py-16">
      <h1 className="font-display text-3xl font-semibold">Model information</h1>
      <p className="mt-3 max-w-xl text-sm text-[var(--text-muted)]">
        Every number on this page is loaded from the metrics actually produced
        by <code className="rounded bg-[var(--surface-alt)] px-1 py-0.5">ml/train.py</code> and{" "}
        <code className="rounded bg-[var(--surface-alt)] px-1 py-0.5">ml/evaluate.py</code> — nothing here is invented.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3">
        {ARCHITECTURE_FACTS.map((fact) => (
          <div key={fact.label} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
            <p className="text-xs text-[var(--text-muted)]">{fact.label}</p>
            <p className="mt-1 text-sm font-medium text-[var(--text)]">{fact.value}</p>
          </div>
        ))}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
          <p className="text-xs text-[var(--text-muted)]">Classes</p>
          <p className="mt-1 text-sm font-medium text-[var(--text)]">{metrics?.num_classes ?? "—"}</p>
        </div>
      </div>

      {notTrained && (
        <div className="mt-10 flex items-start gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
          <AlertTriangle size={20} className="mt-0.5 shrink-0 text-signal-amber" />
          <div>
            <p className="font-display text-base font-semibold">Model not trained yet</p>
            <p className="mt-1 text-sm text-[var(--text-muted)]">
              No metrics were found. Train the model with{" "}
              <code className="rounded bg-[var(--surface-alt)] px-1 py-0.5">python ml/train.py</code>, then optionally run{" "}
              <code className="rounded bg-[var(--surface-alt)] px-1 py-0.5">python ml/evaluate.py</code> for the full
              per-class report. Real numbers will appear here automatically.
            </p>
          </div>
        </div>
      )}

      {error && <p className="mt-10 text-sm text-signal-coral">{error}</p>}

      {metrics && !notTrained && (
        <div className="mt-10 space-y-10">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Metric label="Train accuracy" value={metrics.final_train_accuracy} />
            <Metric label="Validation accuracy" value={metrics.final_val_accuracy} />
            <Metric
              label="Test accuracy"
              value={metrics.overall_test_accuracy ?? metrics.test_accuracy}
            />
            <Metric label="Test AUC" value={metrics.test_auc} decimals={3} suffix="" />
          </div>

          {metrics.per_class && (
            <div>
              <h2 className="font-display text-lg font-semibold">Per-class performance</h2>
              <div className="mt-4 overflow-x-auto rounded-xl border border-[var(--border)]">
                <table className="w-full text-left text-sm">
                  <thead className="bg-[var(--surface-alt)] text-xs uppercase tracking-wide text-[var(--text-muted)]">
                    <tr>
                      <th className="px-4 py-3">Class</th>
                      <th className="px-4 py-3">Precision</th>
                      <th className="px-4 py-3">Recall</th>
                      <th className="px-4 py-3">F1</th>
                      <th className="px-4 py-3">Support</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(metrics.per_class).map(([cls, m]) => (
                      <tr key={cls} className="border-t border-[var(--border)]">
                        <td className="px-4 py-3 font-medium text-[var(--text)]">{cls}</td>
                        <td className="px-4 py-3 font-mono text-[var(--text-muted)]">{m.precision.toFixed(2)}</td>
                        <td className="px-4 py-3 font-mono text-[var(--text-muted)]">{m.recall.toFixed(2)}</td>
                        <td className="px-4 py-3 font-mono text-[var(--text-muted)]">{m.f1_score.toFixed(2)}</td>
                        <td className="px-4 py-3 font-mono text-[var(--text-muted)]">{m.support}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div>
            <h2 className="font-display text-lg font-semibold">Training charts</h2>
            <p className="mt-1 text-sm text-[var(--text-muted)]">
              Generated by the training and evaluation scripts.
            </p>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <ChartImage src={`${API_URL}/assets/training_history.png`} alt="Training accuracy and loss curves" />
              <ChartImage src={`${API_URL}/assets/confusion_matrix.png`} alt="Confusion matrix" />
              <ChartImage src={`${API_URL}/assets/class_distribution.png`} alt="Training set class distribution" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  decimals = 1,
  suffix = "%",
}: {
  label: string;
  value?: number;
  decimals?: number;
  suffix?: string;
}) {
  const display = value === undefined ? "—" : `${(suffix === "%" ? value * 100 : value).toFixed(decimals)}${suffix}`;
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
      <p className="text-xs text-[var(--text-muted)]">{label}</p>
      <p className="mt-1 font-mono text-xl text-signal-violet">{display}</p>
    </div>
  );
}

function ChartImage({ src, alt }: { src: string; alt: string }) {
  const [failed, setFailed] = useState(false);
  if (failed) {
    return (
      <div className="flex h-40 items-center justify-center rounded-xl border border-dashed border-[var(--border)] text-xs text-[var(--text-muted)]">
        Not generated yet
      </div>
    );
  }
  return (
    <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-white">
      <img src={src} alt={alt} className="w-full" onError={() => setFailed(true)} />
    </div>
  );
}
