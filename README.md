# Asset-Energy AI landing page

This folder contains a simple, modern, responsive static landing page:

- `index.html`
- `styles.css`
- `Asset-Energy.ai Energy Policy .png` (existing image)

## Run locally

From this directory:

```bash
python3 -m http.server 5173
```

Then open `http://localhost:5173`.

## News (standalone articles)

Posts live on your site in `news.html`—no LinkedIn embed required.

1. Open `news.html` in an editor.
2. Copy the whole `<article class="news-article">…</article>` block.
3. Paste it above the previous post, change the date, headline, and paragraphs.
4. Update the teaser on `index.html` (hero News panel) if you want the homepage to highlight the new title.
5. Commit and push (GitHub Desktop → **Push origin**).

## Next steps (optional)

- Deploy to Cloudflare Pages (static).
- Replace the `AE` mark with a proper logo and update the favicon.
- Add analytics (Plausible / GA) if you want usage metrics.

## Deploy (Cloudflare Pages + static site)

### 1) Create a Cloudflare Pages project

- In Cloudflare Dashboard → **Pages** → **Create a project**
- Choose **Direct upload** (quick) or connect a Git repo
- Upload / deploy the contents of this folder

### 2) Domain

In Cloudflare Pages → your project → **Custom domains**, add:

- `asset-energy.ai`

Cloudflare will guide you through the DNS records.

