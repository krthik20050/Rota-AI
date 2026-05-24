export const runtime = "nodejs";

const GITHUB_BASE = "https://github.com/krthik20050/Rota-AI/releases/latest/download";

// Map of platform -> release asset filename
const ASSETS: Record<string, { file: string; label: string }> = {
  windows: { file: "RotaAI-Setup.exe", label: "Windows" },
  linux:   { file: "RotaAI.AppImage", label: "Linux" },
};

export async function GET(req: Request) {
  const url = new URL(req.url);
  const platform = (url.searchParams.get("platform") || "windows").toLowerCase();
  const asset = ASSETS[platform] || ASSETS.windows;

  const upstream = await fetch(`${GITHUB_BASE}/${asset.file}`, { redirect: "follow" });

  if (!upstream.ok || !upstream.body) {
    return new Response(`Download unavailable (${asset.label})`, { status: 502 });
  }

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Disposition": `attachment; filename="${asset.file}"`,
      ...(upstream.headers.get("Content-Length")
        ? { "Content-Length": upstream.headers.get("Content-Length")! }
        : {}),
    },
  });
}
