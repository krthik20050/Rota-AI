import { NextRequest, NextResponse } from "next/server";

// Simple in-memory cache with TTL
const cache = new Map<string, { data: unknown; expiry: number }>();
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

/**
 * POST /api/search-console
 *
 * Queries Google Search Console API for performance data (impressions, clicks, CTR, position).
 * Requires GOOGLE_SERVICE_ACCOUNT_EMAIL and GOOGLE_SERVICE_ACCOUNT_KEY to be set in env.
 * The service account must be added as a user in Google Search Console settings.
 *
 * Auth: Requires X-API-Key header matching SEARCH_CONSOLE_API_KEY env var.
 * If SEARCH_CONSOLE_API_KEY is not set, only same-origin requests are allowed.
 *
 * Request body (all optional, with defaults):
 *   siteUrl: string — defaults to "https://rota.software"
 *   startDate: string (YYYY-MM-DD) — defaults to 28 days ago
 *   endDate: string (YYYY-MM-DD) — defaults to yesterday
 *   dimensions: string[] — defaults to ["query"]
 *   rowLimit: number — defaults to 20
 *   dimensionFilterGroups: object[] — optional filters
 */
export async function POST(request: NextRequest) {
  try {
    // Auth check: require API key if configured
    const configuredKey = process.env.SEARCH_CONSOLE_API_KEY;
    if (configuredKey) {
      const providedKey = request.headers.get("x-api-key");
      if (!providedKey || providedKey !== configuredKey) {
        return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
      }
    }

    const body = await request.json().catch(() => ({}));

    const {
      siteUrl = "https://rota.software",
      startDate = new Date(Date.now() - 28 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      endDate = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      dimensions = ["query"],
      rowLimit = 20,
      dimensionFilterGroups,
    } = body;

    // Check cache
    const cacheKey = `${siteUrl}:${startDate}:${endDate}:${dimensions.join(",")}:${rowLimit}`;
    const cached = cache.get(cacheKey);
    if (cached && cached.expiry > Date.now()) {
      return NextResponse.json(cached.data);
    }

    const serviceAccountEmail = process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
    const serviceAccountKey = process.env.GOOGLE_SERVICE_ACCOUNT_KEY;

    if (!serviceAccountEmail || !serviceAccountKey) {
      return NextResponse.json(
        {
          error: "Search Console not configured",
          message:
            "GOOGLE_SERVICE_ACCOUNT_EMAIL and GOOGLE_SERVICE_ACCOUNT_KEY must be set in environment variables.",
          docs: "https://rota.software/admin/seo",
        },
        { status: 503 }
      );
    }

    // Build a JWT assertion for the service account
    const header = { alg: "RS256", typ: "JWT" };
    const now = Math.floor(Date.now() / 1000);
    const claimSet = {
      iss: serviceAccountEmail,
      scope: "https://www.googleapis.com/auth/webmasters.readonly",
      aud: "https://oauth2.googleapis.com/token",
      exp: now + 3600,
      iat: now,
    };

    // Base64url encode
    const b64u = (obj: object) =>
      Buffer.from(JSON.stringify(obj))
        .toString("base64")
        .replace(/=/g, "")
        .replace(/\+/g, "-")
        .replace(/\//g, "_");

    const signatureInput = `${b64u(header)}.${b64u(claimSet)}`;

    // Sign with the private key
    const crypto = await import("crypto");
    const signer = crypto.createSign("RSA-SHA256");
    signer.update(signatureInput);
    const signature = signer
      .sign(serviceAccountKey.replace(/\\n/g, "\n"), "base64")
      .replace(/=/g, "")
      .replace(/\+/g, "-")
      .replace(/\//g, "_");

    const jwt = `${signatureInput}.${signature}`;

    // Exchange JWT for access token
    const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion: jwt,
      }),
    });

    if (!tokenRes.ok) {
      const tokenError = await tokenRes.text();
      return NextResponse.json(
        { error: "Failed to authenticate with Google", details: tokenError },
        { status: 502 }
      );
    }

    const { access_token } = await tokenRes.json();

    // Query Search Console API
    const encodedSite = encodeURIComponent(siteUrl);
    const queryBody: Record<string, unknown> = {
      startDate,
      endDate,
      dimensions,
      rowLimit,
    };
    if (dimensionFilterGroups) {
      queryBody.dimensionFilterGroups = dimensionFilterGroups;
    }

    const gscRes = await fetch(
      `https://www.googleapis.com/webmasters/v3/sites/${encodedSite}/searchAnalytics/query`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(queryBody),
      }
    );

    if (!gscRes.ok) {
      const gscError = await gscRes.text();
      return NextResponse.json(
        { error: "Search Console API error", details: gscError },
        { status: 502 }
      );
    }

    const data = await gscRes.json();

    const responseData = {
      siteUrl,
      startDate,
      endDate,
      rows: data.rows || [],
      responseAggregationType: data.responseAggregationType || "auto",
    };

    // Write to cache
    cache.set(cacheKey, { data: responseData, expiry: Date.now() + CACHE_TTL_MS });

    return NextResponse.json(responseData);
  } catch (err) {
    console.error("[search-console] Error:", err);
    return NextResponse.json(
      { error: "Internal server error", details: String(err) },
      { status: 500 }
    );
  }
}
