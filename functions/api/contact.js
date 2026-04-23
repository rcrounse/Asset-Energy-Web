function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      ...init.headers,
    },
    status: init.status ?? 200,
  });
}

function corsHeaders(request, env) {
  const origin = request.headers.get("origin") || "";
  const allowed = (env.ALLOWED_ORIGIN || "").trim();

  // If ALLOWED_ORIGIN is set, only echo it when it matches.
  // If not set, don't emit ACAO (same-origin fetch doesn't need it).
  if (!allowed) return {};
  if (!origin || origin !== allowed) return {};

  return {
    "access-control-allow-origin": allowed,
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
}

function getUrlHost(request) {
  try {
    return new URL(request.url).hostname;
  } catch {
    return "";
  }
}

function getAllowedHost(env) {
  const allowed = (env.ALLOWED_ORIGIN || "").trim();
  if (!allowed) return "";
  try {
    return new URL(allowed).hostname;
  } catch {
    return "";
  }
}

function originLooksAllowed(request, env) {
  const allowed = (env.ALLOWED_ORIGIN || "").trim();
  if (!allowed) return true;

  const origin = request.headers.get("origin") || "";
  if (origin && origin === allowed) return true;

  // Same-origin browser POSTs sometimes omit `Origin`. Allow if the request host matches ALLOWED_ORIGIN host.
  const allowedHost = getAllowedHost(env);
  const reqHost = request.headers.get("host") || getUrlHost(request);
  if (allowedHost && reqHost && allowedHost === reqHost) return true;

  // Fallback: derive origin from Referer if present.
  const referer = request.headers.get("referer") || "";
  if (referer) {
    try {
      const refOrigin = new URL(referer).origin;
      if (refOrigin === allowed) return true;
    } catch {
      // ignore
    }
  }

  return false;
}

function sanitizeText(value, maxLen) {
  if (typeof value !== "string") return "";
  const v = value.trim();
  return v.length > maxLen ? v.slice(0, maxLen) : v;
}

function isValidEmail(email) {
  if (typeof email !== "string") return false;
  const e = email.trim();
  return e.length >= 5 && e.length <= 254 && e.includes("@") && !e.includes(" ");
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

/**
 * Cloudflare Pages Function
 * Route: /api/contact
 *
 * Sends email via Resend HTTP API (works well on Cloudflare Pages free tier).
 * Docs: https://resend.com/docs/api-reference/emails/send-email
 */
export async function onRequest(context) {
  const { request, env } = context;
  const method = request.method.toUpperCase();

  if (method === "OPTIONS") {
    if (!originLooksAllowed(request, env)) {
      return new Response(null, { status: 403 });
    }

    return new Response(null, {
      status: 204,
      headers: corsHeaders(request, env),
    });
  }

  if (method !== "POST") {
    return json({ ok: false, error: "Method not allowed" }, { status: 405 });
  }

  const headers = corsHeaders(request, env);

  // basic anti-abuse: block unexpected origins if configured
  if (!originLooksAllowed(request, env)) {
    return json({ ok: false, error: "Forbidden origin" }, { status: 403, headers });
  }

  const payload = await readJson(request);
  const name = sanitizeText(payload?.name ?? "", 120);
  const email = sanitizeText(payload?.email ?? "", 254);
  const message = sanitizeText(payload?.message ?? "", 4000);

  if (!name || !isValidEmail(email) || !message) {
    return json({ ok: false, error: "Invalid input" }, { status: 400, headers });
  }

  const to = env.CONTACT_TO || "richardcrounse@gmail.com";
  const from = env.CONTACT_FROM || "no-reply@asset-energy.ai";
  const subject = `New website contact: ${name}`;

  const resendApiKey = env.RESEND_API_KEY || "";

  if (!resendApiKey) {
    return json(
      {
        ok: false,
        error: "Email not configured on the server",
        hint: "Set RESEND_API_KEY in Pages → Settings → Variables and Secrets (Production) as a Secret.",
      },
      { status: 500, headers },
    );
  }

  const text =
    `New contact submission\n\n` +
    `Name: ${name}\n` +
    `Email: ${email}\n\n` +
    `Message:\n${message}\n`;

  // Optional: log to Functions logs (view in Cloudflare dashboard)
  context.waitUntil(
    Promise.resolve().then(() => {
      // eslint-disable-next-line no-console
      console.log("contact_submission", { name, email });
    }),
  );

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      authorization: `Bearer ${resendApiKey}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from,
      to: [to],
      reply_to: email,
      subject,
      text,
    }),
  });

  const apiBody = await resp.json().catch(async () => ({ raw: (await resp.text().catch(() => "")).slice(0, 2000) }));

  if (!resp.ok) {
    return json(
      {
        ok: false,
        error: "Email send failed",
        status: resp.status,
        provider: apiBody,
      },
      { status: 502, headers },
    );
  }

  return json({ ok: true, emailSent: true, id: apiBody?.id ?? null }, { headers });
}

