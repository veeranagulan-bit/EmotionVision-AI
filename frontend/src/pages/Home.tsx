import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Layers, ScanFace, ShieldCheck, Sparkles } from "lucide-react";

const FEATURES = [
  {
    icon: ScanFace,
    title: "Multi-face detection",
    body: "Every face in a photo is found and cropped independently before classification, with a bounding box drawn around each one.",
  },
  {
    icon: Layers,
    title: "Full probability breakdown",
    body: "Not just a single label — see the model's confidence across every supported emotion class, ranked and animated.",
  },
  {
    icon: ShieldCheck,
    title: "Built for honesty",
    body: "Low-confidence results are flagged as uncertain rather than forced into a category, and the app never claims to read minds.",
  },
];

const STEPS = [
  { n: "01", title: "Upload", body: "Drag in a photo, or choose one from your device." },
  { n: "02", title: "Detect", body: "OpenCV locates every face and crops it for the model." },
  { n: "03", title: "Classify", body: "A transfer-learning CNN scores each face against every emotion class." },
  { n: "04", title: "Review", body: "See the primary prediction, confidence, and the full distribution." },
];

export function Home() {
  return (
    <div>
      <section className="grain-bg relative overflow-hidden border-b border-[var(--border)] px-5 py-20 sm:py-28">
        <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] px-3 py-1 text-xs text-[var(--text-muted)]">
              <Sparkles size={12} className="text-signal-violet" /> Transfer-learning CNN · FER-2013
            </span>
            <h1 className="mt-5 font-display text-4xl font-semibold leading-[1.08] tracking-tight sm:text-5xl">
              See the expression.
              <br />
              Understand the moment.
            </h1>
            <p className="mt-5 max-w-md text-base text-[var(--text-muted)]">
              AI-powered facial expression recognition using deep learning and
              computer vision. Upload a photo and get a predicted expression
              for every face, with full confidence scores.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/analyze"
                className="rounded-full bg-spectrum-gradient px-6 py-3 text-sm font-medium text-white shadow-glow transition-transform hover:scale-[1.03]"
              >
                Analyze Image
              </Link>
              <Link
                to="/model"
                className="rounded-full border border-[var(--border)] px-6 py-3 text-sm font-medium text-[var(--text)] transition-colors hover:border-signal-violet/60"
              >
                Explore Model
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="relative mx-auto aspect-square w-full max-w-sm"
          >
            <div className="absolute inset-0 rounded-[2rem] bg-spectrum-gradient opacity-20 blur-3xl" />
            <div className="relative flex h-full w-full items-center justify-center rounded-[2rem] border border-[var(--border)] bg-[var(--surface)]">
              <svg viewBox="0 0 200 200" className="h-2/3 w-2/3" fill="none">
                <circle cx="100" cy="100" r="70" stroke="#8B7FFF" strokeWidth="1.5" strokeDasharray="4 6" opacity="0.5" />
                <circle cx="100" cy="100" r="50" stroke="#FF7A59" strokeWidth="1.5" opacity="0.4" />
                <circle cx="75" cy="85" r="4" fill="#8B7FFF" />
                <circle cx="125" cy="85" r="4" fill="#8B7FFF" />
                <path d="M75 125 Q100 145 125 125" stroke="#45C4B0" strokeWidth="3" strokeLinecap="round" fill="none" />
                <rect x="55" y="60" width="90" height="90" rx="14" stroke="#EDEFF4" strokeOpacity="0.25" strokeWidth="1.5" />
              </svg>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-20">
        <div className="grid gap-6 sm:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
              <Icon size={22} className="text-signal-violet" />
              <h3 className="mt-4 font-display text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm text-[var(--text-muted)]">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-[var(--border)] px-5 py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="font-display text-2xl font-semibold sm:text-3xl">How it works</h2>
          <div className="mt-10 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {STEPS.map((step) => (
              <div key={step.n}>
                <span className="font-mono text-sm text-signal-coral">{step.n}</span>
                <h3 className="mt-2 font-display text-base font-semibold">{step.title}</h3>
                <p className="mt-1 text-sm text-[var(--text-muted)]">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
