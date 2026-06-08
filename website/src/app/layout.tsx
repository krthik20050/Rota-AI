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
        {/* Analytics: Umami (privacy-first) + Microsoft Clarity (heatmaps) are active above.
            Google Analytics is NOT configured by default (no tracking ID set).
            To enable GA4, uncomment below and paste your measurement ID:
            <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX" />
            <script dangerouslySetInnerHTML={{ __html: `window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-XXXXXXXXXX');` }} />
        */}
        {/* Organization + WebSite + SoftwareApplication + FAQPage Schema.org JSON-LD */}
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
              },
              {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "Rota AI",
                "url": "https://rota.software",
                "downloadUrl": "https://github.com/krthik20050/Rota-AI/releases",
                "operatingSystem": "Windows 10/11, macOS 13+, Linux",
                "applicationCategory": "Multimedia",
                "description": "Free, open source voice dictation with AI-powered cleanup, offline mode, no subscriptions. The best Wispr Flow alternative.",
                "offers": {
                  "@type": "Offer",
                  "price": "0",
                  "priceCurrency": "USD",
                  "priceValidUntil": "2027-12-31",
                  "availability": "https://schema.org/InStock"
                },
                "featureList": [
                  "AI-powered text cleanup",
                  "Offline mode via Ollama",
                  "Context-aware app detection",
                  "Voice commands and snippets",
                  "Personal dictionary",
                  "Encrypted API key storage",
                  "Zero telemetry"
                ]
              },
              {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                  {
                    "@type": "Question",
                    "name": "Is this really free?",
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": "Yes. MIT licensed open source. Groq and Gemini both have free tiers that are enough for daily use. Ollama is completely free with no limits. There is no pro plan, no premium tier, no credit card needed."
                    }
                  },
                  {
                    "@type": "Question",
                    "name": "Can I use it without internet?",
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": "Yes. Install Ollama, download a Whisper model (small is 480MB), and Rota works 100% offline. No API keys, no accounts, no internet. Your voice data never leaves your machine."
                    }
                  },
                  {
                    "@type": "Question",
                    "name": "Is Rota AI a free alternative to Wispr Flow?",
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": "Yes, Rota AI is a free, open source alternative to Wispr Flow. It offers similar features like AI-powered text cleanup, context-aware dictation, and works across multiple apps. Unlike Wispr Flow, Rota AI is completely free with no subscriptions, offers offline mode, has zero telemetry, and the full source code is available under MIT license."
                    }
                  },
                  {
                    "@type": "Question",
                    "name": "Is my data private?",
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": "Rota AI has zero telemetry. The desktop app never phones home. Your voice data goes only to the transcription service you choose (Groq, Gemini, or local Ollama). API keys are encrypted at rest using your OS keychain."
                    }
                  },
                  {
                    "@type": "Question",
                    "name": "Does Rota AI work with VS Code?",
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": "Yes. Rota detects VS Code and preserves camelCase, snake_case, and code syntax. Your code comments come out clean without extra punctuation. It also works in terminals and IDEs."
                    }
                  },
                  {
                    "@type": "Question",
                    "name": "What are the system requirements?",
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": "Windows 10/11, macOS 13+, or Linux (Ubuntu 20.04+, Fedora 36+, Arch). 4GB RAM minimum, 8GB recommended. For local GPU transcription: NVIDIA GPU with 4GB+ VRAM. CPU-only works on any modern quad-core."
                    }
                  }
                ]
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
