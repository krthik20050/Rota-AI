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

const SITE_URL = "https://website-omega-lemon-57.vercel.app";

export const metadata: Metadata = {
  title: "Rota AI - Voice Dictation for Windows, Mac & Linux",
  description: "Free, open source voice dictation for Windows, macOS, and Linux. Speak in any app. AI cleans up your text. No subscriptions, no account, no cloud lock.",
  metadataBase: new URL(SITE_URL),
  openGraph: {
    title: "Rota AI - Free Voice Dictation for Windows, Mac & Linux",
    description: "Free, open source Wispr Flow alternative. Speak in any app. AI cleans up your text. No subscriptions, no account, no cloud lock.",
    url: SITE_URL,
    siteName: "Rota AI",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Rota AI - Free Voice Dictation",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Rota AI - Free Voice Dictation for Windows, Mac & Linux",
    description: "Free, open source Wispr Flow alternative. Speak in any app. No subscriptions ever.",
    images: ["/og-image.png"],
  },
  icons: {
    icon: "/favicon.ico",
  },
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
      <head>
        {/* Umami Analytics - replace data-website-id with your ID from umami.is */}
        <script
          defer
          src="https://cloud.umami.is/script.js"
          data-website-id="2c1af14b-5f17-4bb1-bebd-550656ad9201"
        />
        {/* Microsoft Clarity - replace with your Clarity project ID */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","wwl8nuqt5p");`,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col font-sans antialiased bg-[#09090b] text-[#fafafa]">
        {children}
      </body>
    </html>
  );
}
