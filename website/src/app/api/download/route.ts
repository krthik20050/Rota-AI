export const runtime = "nodejs";

const GITHUB_BASE = "https://github.com/krthik20050/Rota-AI/releases/latest/download";

const ASSETS: Record<string, { file: string; label: string }> = {
  windows: { file: "RotaAI-Setup.exe", label: "Windows" },
  linux:   { file: "RotaAI.AppImage", label: "Linux" },
};

export async function GET(req: Request) {
  const url = new URL(req.url);
  const platform = (url.searchParams.get("platform") || "windows").toLowerCase();
  const asset = ASSETS[platform] || ASSETS.windows;

  // Redirect to GitHub releases download
  return Response.redirect(`${GITHUB_BASE}/${asset.file}`, 302);
}
