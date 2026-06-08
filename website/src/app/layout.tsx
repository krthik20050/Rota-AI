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

const SITE_URL = "https://rota.software";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    template: "%s | Rota AI",
    default: "Rota AI — Free Voice Dictation for Windows, Mac & Linux",
  },
  description:
    "Free, open source voice dictation that works in any app. AI-powered cleanup, offline mode, no subscriptions.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Rota AI — Free Voice Dictation",
    description:
      "Free, open source Wispr Flow alternative. Speak in any app. AI cleans up your text. No subscriptions, no account, no cloud lock.",
    url: SITE_URL,
    siteName: "Rota AI",
    type: "website",
    locale: "en_US",
    images: [
      {
        url: "/api/og",
        width: 1200,
        height: 630,
        alt: "Rota AI — Free Voice Dictation",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Rota AI — Free Voice Dictation",
    description:
      "Free, open source voice dictation for Windows, macOS & Linux — no subscriptions, no account needed.",
    images: ["/api/og"],
  },
  icons: {
    icon: "/favicon.ico",
    apple: "/logo.svg",
  },
  manifest: "/site.webmanifest",
  robots: {
    index: true,
    follow: true,
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
        {/* Umami Analytics */}
        <script
          defer
          src="https://cloud.umami.is/script.js"
          data-website-id="2c1af14b-5f17-4bb1-bebd-550656ad9201"
        />
        {/* Microsoft Clarity */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","wwl8nuqt5p");`,
          }}
        />
        {/* Google Analytics 4 - replace G-XXXXXXXXXX with your measurement ID */}
        <script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-XXXXXXXXXX');`,
          }}
        />
        {/* Organization + WebSite Schema.org JSON-LD */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify([
              {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Rota AI",
                "url": "https://rota.software",
                "logo": "https://rota.software/logo.svg",
                "description": "Free, open source voice dictation for Windows, Mac & Linux.",
                "sameAs": [
                  "https://x.com/itsurkk05",
                  "https://github.com/krthik20050/Rota-AI",
                  "https://www.instagram.com/karthikkrishnan000/",
                  "https://www.youtube.com/@Krthikk",
                  "https://www.linkedin.com/in/karthik-krishnan-/"
                ]
              },
              {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "Rota AI",
                "url": "https://rota.software",
                "description": "Free, open source voice dictation that works in any app.",
                "inLanguage": "en-US"
              }
            ]),
          }}
        />
      </head>
      <body className="min-h-full flex flex-col font-sans antialiased bg-[#09090b] text-[#fafafa]">
        {children}
      </body>
    </html>
  );
}
