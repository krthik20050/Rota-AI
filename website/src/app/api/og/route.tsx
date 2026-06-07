import { ImageResponse } from "next/og";

export const runtime = "edge";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get("title") || "Rota AI — Free Voice Dictation";
  const description =
    searchParams.get("description") ||
    "Free, open source voice dictation for Windows, Mac & Linux";

  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: "100%",
          height: "100%",
          background: "#09090b",
          padding: "80px 80px",
        }}
      >
        {/* Subtle grid pattern */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage:
              "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,0.02) 3px,rgba(255,255,255,0.02) 4px)",
          }}
        />

        {/* Accent glow */}
        <div
          style={{
            position: "absolute",
            top: -120,
            left: "50%",
            transform: "translateX(-50%)",
            width: 600,
            height: 400,
            background:
              "radial-gradient(ellipse at center, rgba(228,242,34,0.08) 0%, transparent 60%)",
          }}
        />

        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: "auto" }}>
          <div
            style={{
              width: 48,
              height: 48,
              background: "#e4f222",
              borderRadius: 4,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 28,
              fontWeight: 800,
              color: "#09090b",
            }}
          >
            R
          </div>
          <span style={{ fontSize: 28, color: "#fafafa", fontWeight: 600, letterSpacing: "0.05em" }}>
            ROTA AI
          </span>
        </div>

        {/* Title */}
        <h1
          style={{
            fontSize: 64,
            color: "#fafafa",
            fontWeight: 700,
            lineHeight: 1.1,
            letterSpacing: "-0.02em",
            margin: 0,
            marginBottom: 20,
            maxWidth: 900,
          }}
        >
          {title}
        </h1>

        {/* Description */}
        <p
          style={{
            fontSize: 28,
            color: "#a1a1aa",
            lineHeight: 1.4,
            margin: 0,
            maxWidth: 800,
          }}
        >
          {description}
        </p>

        {/* Bottom bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginTop: "auto",
            paddingTop: 40,
            borderTop: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <span style={{ fontSize: 18, color: "#71717a", letterSpacing: "0.15em" }}>
            FREE · OPEN SOURCE · NO SUBSCRIPTION
          </span>
          <div style={{ flex: 1 }} />
          <span style={{ fontSize: 18, color: "#52525b", letterSpacing: "0.1em" }}>
            rota.software
          </span>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
