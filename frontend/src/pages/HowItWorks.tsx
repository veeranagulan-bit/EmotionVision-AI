import { Camera, Cpu, ScanFace, SlidersHorizontal } from "lucide-react";

const STAGES = [
  {
    icon: Camera,
    title: "1. Image upload",
    body: "You upload a JPG, PNG, or WEBP photo. It's processed in memory and is not stored by default.",
  },
  {
    icon: ScanFace,
    title: "2. Face detection",
    body: "OpenCV scans the image and locates every face, drawing a bounding box around each one it finds.",
  },
  {
    icon: SlidersHorizontal,
    title: "3. Preprocessing",
    body: "Each detected face is cropped, resized to the model's expected input size, and normalized.",
  },
  {
    icon: Cpu,
    title: "4. Classification",
    body: "A transfer-learning CNN scores the cropped face against every emotion class and returns softmax probabilities.",
  },
];

export function HowItWorks() {
  return (
    <div className="mx-auto max-w-4xl px-5 py-16">
      <h1 className="font-display text-3xl font-semibold">How it works</h1>
      <p className="mt-3 max-w-xl text-sm text-[var(--text-muted)]">
        A straightforward computer-vision pipeline: detect, crop, preprocess,
        classify. Nothing about a person's identity is inferred at any stage.
      </p>

      <div className="mt-12 space-y-8">
        {STAGES.map(({ icon: Icon, title, body }, i) => (
          <div key={title} className="relative flex gap-5 pl-1">
            {i < STAGES.length - 1 && (
              <span className="absolute left-[23px] top-12 h-[calc(100%-1rem)] w-px bg-[var(--border)]" />
            )}
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface)] text-signal-violet">
              <Icon size={20} />
            </span>
            <div>
              <h3 className="font-display text-lg font-semibold">{title}</h3>
              <p className="mt-1 max-w-lg text-sm text-[var(--text-muted)]">{body}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-14 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
        <h3 className="font-display text-base font-semibold">A note on confidence</h3>
        <p className="mt-2 text-sm text-[var(--text-muted)]">
          If the model's top probability falls below a configurable threshold
          (50% by default), the result is shown as <strong className="text-[var(--text)]">Uncertain</strong> rather
          than being forced into a category the model isn't confident about.
        </p>
      </div>
    </div>
  );
}
