import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="border-t border-[var(--border)] py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 text-sm text-[var(--text-muted)] sm:flex-row sm:items-center sm:justify-between">
        <p>EmotionVision AI — a facial-expression classifier, not a mind reader.</p>
        <div className="flex flex-wrap gap-5">
          <Link to="/about" className="hover:text-[var(--text)]">
            Responsible AI
          </Link>
          <Link to="/model" className="hover:text-[var(--text)]">
            Model
          </Link>
          <a href="https://github.com/" target="_blank" rel="noreferrer" className="hover:text-[var(--text)]">
            Source on GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
