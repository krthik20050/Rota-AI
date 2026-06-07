import Link from "next/link";

export const metadata = {
  title: "404 - Page Not Found | Rota AI",
  description: "The page you are looking for does not exist.",
};

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col items-center justify-center px-6 text-center">
      <div className="max-w-md">
        <div className="mb-8 flex justify-center">
          <Link href="/">
            <img src="/logo.svg" alt="Rota AI" className="h-16 w-auto" />
          </Link>
        </div>
        <h1
          className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-4"
          style={{ fontSize: "clamp(72px, 15vw, 120px)", color: "#e4f222" }}
        >
          404
        </h1>
        <p className="text-sm text-[#a1a1aa] mb-8 leading-relaxed">
          This page does not exist. It might have been moved, deleted, or the URL
          might be incorrect.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 text-xs font-semibold uppercase tracking-[0.15em] transition-all hover:opacity-90"
          style={{ background: "#e4f222", color: "#000", borderRadius: 2 }}
        >
          ← Back to home
        </Link>
      </div>
    </div>
  );
}
