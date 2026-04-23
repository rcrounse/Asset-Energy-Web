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

