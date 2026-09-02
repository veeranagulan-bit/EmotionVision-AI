import { Eye, HeartHandshake, ShieldCheck } from "lucide-react";

export function About() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-16">
      <h1 className="font-display text-3xl font-semibold">About &amp; Responsible AI</h1>
      <p className="mt-3 text-sm text-[var(--text-muted)]">
        EmotionVision AI is a facial-expression classifier built as a computer-vision
        portfolio project. It's designed to be technically honest about what it can
        and can't tell you.
      </p>

      <section className="mt-12">
        <h2 className="flex items-center gap-2 font-display text-xl font-semibold">
          <Eye size={20} className="text-signal-violet" /> What this is — and isn't
        </h2>
        <ul className="mt-4 space-y-3 text-sm text-[var(--text-muted)]">
          <li>
            The model classifies the visual pattern of a facial expression in a
            photo. It does not, and cannot, determine a person's true internal
            emotional state.
          </li>
          <li>
            Lighting, pose, occlusion, image quality, camera angle, cultural
            expression differences, and dataset bias can all affect predictions.
          </li>
          <li>Every prediction is probabilistic, and low-confidence results are labeled "Uncertain" rather than forced into a category.</li>
          <li>The model should never be used for medical or psychological diagnosis.</li>
        </ul>
      </section>

      <section className="mt-12">
        <h2 className="flex items-center gap-2 font-display text-xl font-semibold">
          <ShieldCheck size={20} className="text-signal-violet" /> Where it should not be used
        </h2>
        <p className="mt-4 text-sm text-[var(--text-muted)]">
          This project is not built or validated for high-impact decisions, and
          should not be used for hiring, policing, surveillance, insurance
          decisions, or any other consequential judgment about a real person.
          It also does not perform facial recognition or identity matching —
          it has no way to tell who someone is, only what expression a
          detected face appears to show.
        </p>
      </section>

      <section className="mt-12">
        <h2 className="flex items-center gap-2 font-display text-xl font-semibold">
          <HeartHandshake size={20} className="text-signal-violet" /> Privacy first
        </h2>
        <p className="mt-4 text-sm text-[var(--text-muted)]">
          Images are processed only for facial-expression analysis. Uploaded
          photos are handled in memory wherever possible and are not stored
          by the backend by default; if a temporary file is ever required
          during processing, it's deleted immediately afterward.
        </p>
      </section>
    </div>
  );
}
