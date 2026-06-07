import { LandingPage } from "@/components/LandingPage"

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Rota AI",
  operatingSystem: "Windows, macOS, Linux",
  applicationCategory: "Multimedia",
  description:
    "Free, open source voice dictation that works in any app. AI-powered cleanup, offline mode, no subscriptions.",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
  },
  author: {
    "@type": "Person",
    name: "Rota AI Contributors",
  },
};

export default function HomePage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <LandingPage />
    </>
  );
}
