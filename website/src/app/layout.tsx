import type { Metadata } from "next";
import { Geist, Geist_Mono, Cormorant } from "next/font/google";
import "./globals.css";

const geist = Geist({
  variable: "--font-geist",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const cormorant = Cormorant({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const geistMono = Geist_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Rota AI — Voice Dictation for Windows",
  description: "Free, open source voice dictation for Windows. Speak in any app. AI cleans up your text. No subscriptions, no account, no cloud lock.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geist.variable} ${geistMono.variable} ${cormorant.variable} h-full`}
    >
      <body className="min-h-full flex flex-col font-sans antialiased bg-[#09090b] text-[#fafafa]">
        {children}
      </body>
    </html>
  );
}
