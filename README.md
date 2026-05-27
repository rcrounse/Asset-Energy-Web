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

- `news.html` — list of posts (teaser + link)
- `news/your-article-slug.html` — full article page (edit the HTML body here)

To add a post:

1. Copy `news/you-can-run-but-you-cant-hide-co2.html` to a new file under `news/`.
2. Edit the title and all `<p>` paragraphs in `.article-full-body`.
3. Add a matching preview block to `news.html` with a link to your new file.
4. Commit and push (GitHub Desktop → **Push origin**).

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

