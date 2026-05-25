export const runtime = "nodejs";

const GITHUB_BASE = "https://github.com/krthik20050/Rota-AI/releases/latest/download";

const ASSETS: Record<string, { file: string; label: string }> = {
  windows: { file: "RotaAI-Setup.exe", label: "Windows" },
  macos:   { file: "RotaAI-macOS.zip", label: "macOS" },
  mac:     { file: "RotaAI-macOS.zip", label: "macOS" },
  linux:   { file: "RotaAI.AppImage", label: "Linux" },
};

export async function GET(req: Request) {
  const url = new URL(req.url);
  const platform = (url.searchParams.get("platform") || "windows").toLowerCase();
  const asset = ASSETS[platform] || ASSETS.windows;

  const downloadUrl = `${GITHUB_BASE}/${asset.file}`;

  // Fetch the file from GitHub (follows redirects)
  const upstream = await fetch(downloadUrl, { redirect: "follow" });

  if (!upstream.ok || !upstream.body) {
    return new Response("Download unavailable", { status: 502 });
  }

  const contentType = upstream.headers.get("content-type") ?? "application/octet-stream";

  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": contentType,
      "Content-Disposition": `attachment; filename="${asset.file}"`,
      // Forward content-length if present so browser shows progress
      ...(upstream.headers.get("content-length")
        ? { "Content-Length": upstream.headers.get("content-length")! }
        : {}),
    },
  });
}
