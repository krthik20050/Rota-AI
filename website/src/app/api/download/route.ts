import { NextResponse } from "next/server";

const LATEST_EXE =
  "https://github.com/krthik20050/Rota-AI/releases/download/v1.0.0/RotaAI.exe";

export function GET() {
  return NextResponse.redirect(LATEST_EXE, {
    headers: {
      "Content-Disposition": 'attachment; filename="RotaAI.exe"',
    },
  });
}
