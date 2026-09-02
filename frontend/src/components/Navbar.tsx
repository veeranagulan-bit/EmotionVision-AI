import { useState } from "react";
import { NavLink } from "react-router-dom";
import { Menu, ScanFace, X } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/analyze", label: "Analyze" },
  { to: "/how-it-works", label: "How It Works" },
  { to: "/model", label: "Model" },
  { to: "/about", label: "About" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--bg)]/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
        <NavLink to="/" className="flex items-center gap-2 font-display text-lg font-semibold tracking-tight" onClick={() => setOpen(false)}>
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-spectrum-gradient text-[var(--bg)]">
            <ScanFace size={18} />
          </span>
          EmotionVision <span className="text-signal-violet">AI</span>
        </NavLink>

        <nav className="hidden items-center gap-7 md:flex">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `text-sm transition-colors ${
                  isActive ? "text-[var(--text)]" : "text-[var(--text-muted)] hover:text-[var(--text)]"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <a
            href="https://github.com/"
            target="_blank"
            rel="noreferrer"
            className="text-sm text-[var(--text-muted)] transition-colors hover:text-[var(--text)]"
          >
            GitHub
          </a>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <NavLink
            to="/analyze"
            className="rounded-full bg-spectrum-gradient px-4 py-2 text-sm font-medium text-white shadow-glow transition-transform hover:scale-[1.03]"
          >
            Analyze Image
          </NavLink>
        </div>

        <button
          className="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--border)] md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>

      {open && (
        <nav className="flex flex-col gap-1 border-t border-[var(--border)] px-5 py-4 md:hidden">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm ${
                  isActive ? "bg-[var(--surface)] text-[var(--text)]" : "text-[var(--text-muted)]"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <div className="mt-2 flex items-center justify-between px-3">
            <ThemeToggle />
            <NavLink
              to="/analyze"
              onClick={() => setOpen(false)}
              className="rounded-full bg-spectrum-gradient px-4 py-2 text-sm font-medium text-white"
            >
              Analyze Image
            </NavLink>
          </div>
        </nav>
      )}
    </header>
  );
}
