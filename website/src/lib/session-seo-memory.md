# SEO Session Memory — June 9, 2026

## Completed This Session

### Schema Markup (highest SEO impact)
- [x] **SoftwareApplication schema** (layout.tsx) — price=$0, 7 features, cross-platform OS support
- [x] **FAQPage schema** (layout.tsx) — 6 Q&A pairs including "free alternative to Wispr Flow"
- [x] **ItemList schema** (blog/page.tsx) — All 34 blog posts as structured list items
- [x] **Organization + WebSite** — Already existed, updated with software details

### Technical SEO
- [x] **Google Analytics placeholder** — Removed broken `G-XXXXXXXXXX` code (was polluting analytics)
- [x] **Blog metadata** — Updated title to avoid template redundancy, description targets voice dictation keywords
- [x] **Footer internal links** — Added "Compare" column with links to `/vs/wispr-flow`, `/vs/superwhisper`, and comparison blog posts
- [x] **Footer grid** — Changed from `lg:grid-cols-5` to `lg:grid-cols-6` to accommodate new column

### GitHub SEO
- [x] **GitHub topics set** (15 total): `voice-dictation`, `speech-to-text`, `wispr-flow-alternative`, `whisper`, `open-source`, `python`, `windows`, `pyqt6`, `voice-typing`, `dictation`, `privacy-first`, `desktop-app`, `offline-speech-recognition`, `free-alternative`, `ai-dictation`
- [x] **README optimized** — Added HTML SEO meta comment, front-loaded "free alternative to Wispr Flow" in subtitle

### Search Console Dashboard (built for future use)
- [x] **API route** (`/api/search-console`) — Proxies Google Search Console data. JWT auth, 5-min cache, X-API-Key protection
- [x] **Dashboard page** (`/admin/seo`) — Summary cards, period selector (7d/28d/90d), ranked query table, color-coded positions, setup instructions when not configured

## Pending — Needs User Action Tomorrow

### 🔴 Priority 1: URL Inspection in Search Console (5 minutes)
Go to [search.google.com/search-console](https://search.google.com/search-console) → click `rota.software` → use the URL inspection bar at top to submit these 5 URLs one at a time:
1. `https://rota.software`
2. `https://rota.software/vs/wispr-flow`
3. `https://rota.software/vs/superwhisper`
4. `https://rota.software/blog`
5. `https://rota.software/blog/wispr-flow-alternatives-that-are-actually-free-in-2026`

For each: paste URL → press Enter → click "Request Indexing"

### 🟡 Priority 2: Directory Submissions (15 minutes)
Submit Rota AI to these directories for backlinks:
| Directory | URL | What to do |
|-----------|-----|------------|
| AlternativeTo | alternativeto.net | Sign up → "Suggest new application" |
| SaaSHub | saashub.com/services/submit | Sign up → "Submit a Product" |
| G2 | g2.com/products/new | Sign up → "Add a product" |

### 🟡 Priority 3: Awesome List PRs on GitHub
Submit PRs adding Rota AI to:
1. **sindresorhus/awesome-whisper** — Edit README.md, add under "Tools" section
2. **primaprashant/awesome-voice-typing** — Edit README.md, add to list

### 🟢 Priority 4: Search Console Dashboard Setup (after user has Google Cloud access)
1. Create service account in Google Cloud Console
2. Add to Search Console as user
3. Add env vars to Vercel: `GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_SERVICE_ACCOUNT_KEY`, `SEARCH_CONSOLE_API_KEY`

## Git State
- Branch: `feat/website-logo-rebrand`
- Latest commit: `376d888` — `feat(seo): add Search Console API route with caching + auth, build SEO dashboard page`
- Previous commit: `f9845a5` — `feat(seo): add SoftwareApplication, FAQPage, ItemList schemas; add comparison footer links; fix GA placeholder`
- Earlier commit: `371bbc0` — `fix: remove broken GA placeholder, optimize README SEO`
- All pushed to origin. Need PR to merge into `main` for Vercel deploy.

## Vercel Notes
- Root directory fixed from `.` to `website/`
- Production deploy succeeded
- Site live at rota.software with 45 URLs in sitemap
- Sitemap submitted to Google Search Console ✅
