"use client";

import * as React from "react";
import Link from "next/link";

interface GscRow {
  keys: string[];
  clicks: number;
  impressions: number;
  ctr: number;
  position: number;
}

function formatNumber(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K";
  return n.toLocaleString();
}

function formatCtr(ctr: number): string {
  return (ctr * 100).toFixed(1) + "%";
}

function positionColor(pos: number): string {
  if (pos <= 3) return "#22c55e";    // green — top 3
  if (pos <= 10) return "#e4f222";   // lime — page 1
  if (pos <= 20) return "#f97316";   // orange — page 2
  return "#ef4444";                  // red — beyond
}

function Row({ row, rank }: { row: GscRow; rank: number }) {
  return (
    <tr className="border-b border-white/[.03] hover:bg-white/[.02] transition-colors">
      <td className="py-2.5 px-3 text-[11px] font-mono text-zinc-600">{rank}</td>
      <td className="py-2.5 px-3 text-xs text-[#fafafa] max-w-[320px] truncate" title={row.keys[0]}>
        {row.keys[0]}
      </td>
      <td className="py-2.5 px-3 text-xs text-right text-zinc-300">{formatNumber(row.clicks)}</td>
      <td className="py-2.5 px-3 text-xs text-right text-zinc-300">{formatNumber(row.impressions)}</td>
      <td className="py-2.5 px-3 text-xs text-right text-zinc-300">{formatCtr(row.ctr)}</td>
      <td className="py-2.5 px-3 text-xs text-right font-mono" style={{ color: positionColor(row.position) }}>
        {row.position.toFixed(1)}
      </td>
    </tr>
  );
}

export default function SeoDashboard() {
  const [rows, setRows] = React.useState<GscRow[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [period, setPeriod] = React.useState("28d");
  const [version, setVersion] = React.useState(0);

  /** Fetch data and return it (no setState). All setState is in promise handlers below. */
  const fetchData = React.useCallback(async (p: string): Promise<GscRow[]> => {
    const now = new Date();
    const endDate = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    let startDate: string;

    switch (p) {
      case "7d":  startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10); break;
      case "90d": startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10); break;
      default:    startDate = new Date(now.getTime() - 28 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    }

    const res = await fetch("/api/search-console", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ startDate, endDate, dimensions: ["query"], rowLimit: 50 }),
    });
    const data = await res.json();

    if (!res.ok) {
      if (res.status === 503) throw new Error("NOT_CONFIGURED");
      throw new Error(data.error || "Failed to fetch data");
    }
    return data.rows || [];
  }, []);

  /* Fetch on mount, period change & retry. All setState in async promise handlers. */
  React.useEffect(() => {
    let mounted = true;
    fetchData(period)
      .then((rows) => { if (mounted) { setRows(rows); setError(null); } })
      .catch((err: Error) => { if (mounted) { setRows([]); setError(err.message); } })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period, version]);

  const handlePeriodChange = React.useCallback((p: string) => {
    setPeriod(p);
    setLoading(true);
    setError(null);
    setVersion(0);
  }, []);

  const handleRetry = React.useCallback(() => {
    setLoading(true);
    setError(null);
    setVersion((v) => v + 1);
  }, []);

  const totalClicks = rows.reduce((s, r) => s + r.clicks, 0);
  const totalImpressions = rows.reduce((s, r) => s + r.impressions, 0);
  const avgPosition = rows.length > 0
    ? rows.reduce((s, r) => s + r.position * r.impressions, 0) / totalImpressions
    : 0;
  const avgCtr = totalImpressions > 0 ? totalClicks / totalImpressions : 0;

  const page1Count = rows.filter((r) => r.position <= 10).length;
  const page1Clicks = rows.filter((r) => r.position <= 10).reduce((s, r) => s + r.clicks, 0);

  return (
    <div className="min-h-screen bg-[#09090b] text-[#fafafa]">
      {/* Nav */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 h-14"
        style={{
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(9,9,11,0.92)",
          backdropFilter: "blur(16px)",
        }}
      >
        <Link href="/" className="flex items-center">
          <img src="/logo.svg" alt="Rota AI" className="h-8 w-auto" />
        </Link>
        <div className="flex items-center gap-6 text-xs uppercase tracking-[0.15em] text-[#71717a]">
          <Link href="/" className="hover:text-[#fafafa] transition-colors">Home</Link>
          <span className="text-[#fafafa]">SEO Dashboard</span>
        </div>
      </nav>

      <div className="pt-24 px-6 sm:px-10 pb-20 max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <p className="text-[11px] uppercase tracking-[0.2em] text-[#e4f222] font-mono mb-3">Analytics</p>
          <h1 className="font-display uppercase tracking-[0.02em] leading-[0.92] mb-3"
            style={{ fontSize: "clamp(28px, 4vw, 48px)" }}>
            Search Console
          </h1>
          <p className="text-sm text-zinc-500 max-w-lg leading-relaxed">
            Top queries by impressions, clicks, and average position. Data from Google Search Console.
          </p>
        </div>

        {/* Period selector */}
        <div className="flex items-center gap-2 mb-8">
          {["7d", "28d", "90d"].map((p) => (
            <button
              key={p}
              onClick={() => handlePeriodChange(p)}
              className="px-3 py-1.5 text-[11px] font-mono uppercase tracking-wider rounded-sm transition-all"
              style={{
                background: period === p ? "rgba(228,242,34,0.1)" : "rgba(255,255,255,0.03)",
                border: `1px solid ${period === p ? "rgba(228,242,34,0.3)" : "rgba(255,255,255,0.06)"}`,
                color: period === p ? "#e4f222" : "#50545a",
              }}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {[
            { label: "Total Clicks", value: formatNumber(totalClicks), color: "#e4f222" },
            { label: "Impressions", value: formatNumber(totalImpressions), color: "#fafafa" },
            { label: "Avg Position", value: avgPosition.toFixed(1), color: positionColor(avgPosition) },
            { label: "Avg CTR", value: formatCtr(avgCtr), color: "#22c55e" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="p-4 rounded-sm"
              style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}
            >
              <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono mb-1">{stat.label}</div>
              <div className="text-lg font-semibold" style={{ color: stat.color }}>{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Insight: page 1 keywords */}
        <div
          className="mb-8 p-4 rounded-sm text-xs leading-relaxed"
          style={{ background: "rgba(228,242,34,0.03)", border: "1px solid rgba(228,242,34,0.12)", color: "#a1a1aa" }}
        >
          <span className="text-[#e4f222] font-semibold">{page1Count}</span> keywords on page 1 (position ≤ 10)
          generating <span className="text-[#e4f222] font-semibold">{formatNumber(page1Clicks)}</span> clicks.
          {page1Count > 0
            ? " These are your strongest opportunities — optimize these pages to push them higher."
            : " No keywords on page 1 yet. Focus on long-tail keywords with lower competition."}
        </div>

        {/* Table */}
        {error === "NOT_CONFIGURED" ? (
          <div
            className="p-8 rounded-sm text-center"
            style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <p className="text-sm text-zinc-400 mb-4">Search Console API not configured yet.</p>
            <div className="text-left max-w-lg mx-auto space-y-3 text-xs text-zinc-500 leading-relaxed">
              <p><strong className="text-[#fafafa]">To set up GSC API access:</strong></p>
              <ol className="list-decimal pl-4 space-y-2">
                <li>Go to <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer"
                  className="text-[#e4f222] hover:underline">Google Cloud Console</a> → create a project → enable the Search Console API</li>
                <li>Create a <strong>Service Account</strong> (IAM &amp; Admin → Service Accounts → Create) and download the JSON key</li>
                <li>Copy the service account email, go to <a href="https://search.google.com/search-console" target="_blank" rel="noopener noreferrer"
                  className="text-[#e4f222] hover:underline">Google Search Console</a> → Settings → Users and permissions → Add the service account email as a user</li>
                <li>Copy the private key from the JSON file and add these to Vercel env vars (or .env.local):
                  <pre className="mt-2 p-2 rounded-sm text-[10px] font-mono" style={{ background: "rgba(0,0,0,0.3)" }}>
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-sa@project.iam.gserviceaccount.com{'\n'}
GOOGLE_SERVICE_ACCOUNT_KEY=&quot;-----BEGIN PRIVATE KEY-----\nMIIEv...\n-----END PRIVATE KEY-----&quot;
                  </pre>
                </li>
                <li>Refresh this page — data will appear automatically</li>
              </ol>
            </div>
          </div>
        ) : loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-6 h-6 border-2 border-[#e4f222]/30 border-t-[#e4f222] rounded-full animate-spin mb-3" />
            <p className="text-xs text-zinc-500">Loading Search Console data...</p>
          </div>
        ) : error ? (
          <div className="p-6 rounded-sm text-center" style={{ background: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.2)" }}>
            <p className="text-xs text-red-400">{error}</p>
            <button onClick={() => handleRetry()}
              className="mt-3 text-xs text-zinc-400 hover:text-white transition-colors underline">
              Try again
            </button>
          </div>
        ) : rows.length === 0 ? (
          <div className="p-6 rounded-sm text-center" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
            <p className="text-xs text-zinc-500">No data found for this period. Check your site URL in Search Console settings.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/[.06]">
                  <th className="text-left py-2.5 px-3 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">#</th>
                  <th className="text-left py-2.5 px-3 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">Query</th>
                  <th className="text-right py-2.5 px-3 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">Clicks</th>
                  <th className="text-right py-2.5 px-3 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">Impressions</th>
                  <th className="text-right py-2.5 px-3 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">CTR</th>
                  <th className="text-right py-2.5 px-3 text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono">Position</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <Row key={row.keys[0]} row={row} rank={i + 1} />
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Quick access links */}
        <div className="mt-12 pt-8" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <h3 className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-mono mb-3">Quick Links</h3>
          <div className="flex flex-wrap gap-3">
            <a href="https://search.google.com/search-console" target="_blank" rel="noopener noreferrer"
              className="text-xs text-zinc-500 hover:text-[#e4f222] transition-colors underline underline-offset-2">
              Google Search Console →
            </a>
            <a href="https://analytics.google.com" target="_blank" rel="noopener noreferrer"
              className="text-xs text-zinc-500 hover:text-[#e4f222] transition-colors underline underline-offset-2">
              Google Analytics →
            </a>
            <Link href="/sitemap.xml" className="text-xs text-zinc-500 hover:text-[#e4f222] transition-colors underline underline-offset-2">
              View Sitemap →
            </Link>
            <Link href="/blog" className="text-xs text-zinc-500 hover:text-[#e4f222] transition-colors underline underline-offset-2">
              Blog →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
