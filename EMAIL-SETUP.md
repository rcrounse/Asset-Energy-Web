# Email for asset-energy.ai (about 10 minutes)

You do **not** need website code to email `editor@utilitydive.com`. You need a normal email address on your domain, e.g. **`contact@asset-energy.ai`**, that forwards to your personal inbox.

Your domain is already on **Cloudflare**, so use **Email Routing** (free).

## Part 1 — Receive mail at contact@asset-energy.ai

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com).
2. Select domain **`asset-energy.ai`**.
3. Left menu → **Email** → **Email Routing**.
4. Click **Get started** (if shown).
5. Under **Routing rules** → **Create address**:
   - **Custom address:** `contact`
   - **Action:** Send to an email → your personal inbox (e.g. Gmail)
6. Cloudflare will add the required **DNS records** — click **Add records** / confirm.

Wait a few minutes. Send a test from your phone to **contact@asset-energy.ai** and confirm it arrives in your inbox.

## Part 2 — Send mail *as* contact@asset-energy.ai (for Utility Dive pitch)

### Option A — Gmail “Send mail as” (recommended)

1. Open Gmail → **Settings** (gear) → **See all settings** → **Accounts and Import**.
2. **Send mail as** → **Add another email address**.
3. Name: `Asset-Energy AI`
4. Email: `contact@asset-energy.ai`
5. Uncheck “Treat as alias” if you want replies clearly separated (optional).
6. Gmail sends a verification code → it arrives via Cloudflare forward to your inbox → paste the code.
7. For **SMTP server**, Gmail often completes setup automatically. If asked, use Gmail’s default SMTP with your Gmail login.

When you compose email to `editor@utilitydive.com`, choose **From: contact@asset-energy.ai**.

### Option B — Send from Gmail without “Send as” (quick test)

You can email Utility Dive **from your Gmail** today. Use **Reply-To: contact@asset-energy.ai** only after Part 1 works (optional in Gmail compose → More options).

## Part 3 — Formspree (contact form on the website)

The site form still uses Formspree. In [Formspree](https://formspree.io) → your form → **Settings**:

- Set notification email to the inbox that receives **contact@asset-energy.ai** (your forwarded Gmail).

No code change required.

## Part 4 — Website

The site already shows **contact@asset-energy.ai** in the contact section and footer (after you push the latest commit).

---

## Send the Utility Dive pitch

1. Open Gmail (or Mail).
2. **To:** `editor@utilitydive.com`
3. **From:** `contact@asset-energy.ai` (after Part 2)
4. Paste the pitch from the chat / README.
5. Include link: `https://asset-energy.ai/news/you-can-run-but-you-cant-hide-co2.html`
6. Send.

---

## Troubleshooting

| Problem | Fix |
|--------|-----|
| Verification email never arrives | Check Cloudflare Email Routing is **Enabled** and DNS records show **Active** |
| Can receive but not send as @asset-energy.ai | Finish Gmail “Send mail as” or use Gmail + professional signature with contact@ in signature |
| Formspree still goes to old email | Update notification address in Formspree dashboard |

Cloudflare Email Routing docs: https://developers.cloudflare.com/email-routing/
