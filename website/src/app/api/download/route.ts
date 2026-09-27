export const runtime = "nodejs";

// /api/download?platform=windows|macos|linux
//
// Resolves the requested platform against the *actual* assets published on the
// latest GitHub release, instead of hardcoding filenames. The hardcoded names
// drifted from what the release pipeline uploaded (the release ships
// "RotaAI.exe" while this route demanded "RotaAI-Setup.exe"), so every download
// button on the website 404'd upstream and surfaced as a 502.
//
// We redirect (302) to GitHub's browser_download_url rather than proxying the
// binary: the installer is ~300 MB and streaming it through a serverless
// function risks function timeouts and double bandwidth.

const REPO = "krthik20050/Rota-AI";
const RELEASES_API = `https://api.github.com/repos/${REPO}/releases/latest`;
const RELEASES_PAGE = `https://github.com/${REPO}/releases/latest`;
const REQUEST_TIMEOUT_MS = 5000;

/** Exact asset filenames to look for, in priority order per platform. */
const EXACT_NAMES: Record<string, string[]> = {
  windows: ["RotaAI-Setup.exe", "RotaAI.exe"],
  macos: ["RotaAI-macOS.zip", "RotaAI-macOS.dmg"],
  linux: ["RotaAI.AppImage"],
};

/** Extension-based fallback when no exact name matches (e.g. renamed builds). */
const EXTENSION_HINTS: Record<string, RegExp> = {
  windows: /\.exe$/i,
  macos: /\.(zip|dmg)$/i,
  linux: /\.appimage$/i,
};

interface ReleaseAsset {
  name: string;
  browser_download_url: string;
}

function normalizePlatform(raw: string | null): string {
  const value = (raw ?? "windows").trim().toLowerCase();
  if (value === "win") return "windows";
  if (value === "mac" || value === "darwin" || value === "osx") return "macos";
  return value in EXACT_NAMES ? value : "windows";
}

function findAsset(assets: ReleaseAsset[], platform: string): ReleaseAsset | null {
  for (const name of EXACT_NAMES[platform] ?? []) {
    const exact = assets.find((a) => a.name.toLowerCase() === name.toLowerCase());
    if (exact) return exact;
  }
  const hint = EXTENSION_HINTS[platform];
  if (hint) {
    return assets.find((a) => hint.test(a.name)) ?? null;
  }
  return null;
}

/**
 * Look up the latest release on GitHub and pick the best asset for the
 * platform. Returns null on any failure (network, rate limit, no matching
 * asset) — the caller falls back to the releases page.
 */
async function resolveAssetUrl(platform: string): Promise<string | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(RELEASES_API, {
      headers: {
        Accept: "application/vnd.github+json",
        "User-Agent": "rota-download-resolver/1.0",
      },
      signal: controller.signal,
      cache: "no-store",
    });
    if (!res.ok) return null;

    const release = (await res.json()) as { assets?: ReleaseAsset[] };
    const assets = release.assets ?? [];
    const asset = findAsset(assets, platform);
    return asset?.browser_download_url ?? null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const platform = normalizePlatform(url.searchParams.get("platform"));

  const assetUrl = await resolveAssetUrl(platform);
  if (assetUrl) {
    return Response.redirect(assetUrl, 302);
  }

  // Release lookup failed or no matching asset: send users to the releases
  // page so they can grab whatever *is* published, instead of a dead 502.
  return Response.redirect(RELEASES_PAGE, 302);
}
