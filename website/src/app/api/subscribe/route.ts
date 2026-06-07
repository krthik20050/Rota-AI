export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    // Accept both JSON and form-encoded data
    let email: string | null = null;
    const contentType = req.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const body = await req.json();
      email = body.email;
    } else {
      const formData = await req.formData();
      email = formData.get("email") as string | null;
    }

    if (!email || typeof email !== "string") {
      return Response.json({ error: "Email is required" }, { status: 400 });
    }

    const apiKey = process.env.BUTTONDOWN_API_KEY;

    // If no API key configured, just return success (for development)
    if (!apiKey) {
      console.log("[subscribe] No BUTTONDOWN_API_KEY configured, skipping");
      return Response.json({ success: true, note: "development mode" });
    }

    const response = await fetch("https://api.buttondown.email/v1/subscribers", {
      method: "POST",
      headers: {
        Authorization: `Token ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, tags: ["website-signup"] }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error("[subscribe] Buttondown error:", errorData);
      return Response.json({ error: "Failed to subscribe" }, { status: 500 });
    }

    // Redirect back to the referring page if it was a form POST (not fetch)
    const referer = req.headers.get("referer") || "/blog";
    if (contentType.includes("application/json")) {
      return Response.json({ success: true });
    }
    return Response.redirect(referer, 302);
  } catch (error) {
    console.error("[subscribe] Error:", error);
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}
