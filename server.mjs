import http from "node:http";
import { readFile, writeFile, appendFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT || 5173);
const HOST = process.env.HOST || "127.0.0.1";

const PUBLIC_FILES = new Map([
  ["/", "index.html"],
  ["/index.html", "index.html"],
  ["/styles.css", "styles.css"],
  ["/favicon.svg", "favicon.svg"],
  ["/robots.txt", "robots.txt"],
  ["/sitemap.xml", "sitemap.xml"],
  ["/Asset-Energy.ai%20Energy%20Policy%20.png", "Asset-Energy.ai Energy Policy .png"],
]);

function send(res, status, headers, body) {
  res.writeHead(status, headers);
  res.end(body);
}

function contentTypeFor(file) {
  if (file.endsWith(".html")) return "text/html; charset=utf-8";
  if (file.endsWith(".css")) return "text/css; charset=utf-8";
  if (file.endsWith(".svg")) return "image/svg+xml";
  if (file.endsWith(".txt")) return "text/plain; charset=utf-8";
  if (file.endsWith(".xml")) return "application/xml; charset=utf-8";
  if (file.endsWith(".png")) return "image/png";
  return "application/octet-stream";
}

async function readJsonBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function isValidEmail(email) {
  if (typeof email !== "string") return false;
  const e = email.trim();
  return e.length >= 5 && e.length <= 254 && e.includes("@") && !e.includes(" ");
}

function sanitizeText(value, maxLen) {
  if (typeof value !== "string") return "";
  const v = value.trim();
  return v.length > maxLen ? v.slice(0, maxLen) : v;
}

const server = http.createServer(async (req, res) => {
  try {
    if (!req.url) return send(res, 400, { "Content-Type": "text/plain; charset=utf-8" }, "Bad Request");
    const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
    const pathname = url.pathname;

    if (pathname === "/api/contact" && req.method === "POST") {
      const payload = await readJsonBody(req);

      const name = sanitizeText(payload?.name ?? "", 120);
      const email = sanitizeText(payload?.email ?? "", 254);
      const message = sanitizeText(payload?.message ?? "", 4000);

      if (!name || !isValidEmail(email) || !message) {
        return send(
          res,
          400,
          { "Content-Type": "application/json; charset=utf-8" },
          JSON.stringify({ ok: false, error: "Invalid input" }),
        );
      }

      const record = {
        receivedAt: new Date().toISOString(),
        name,
        email,
        message,
        ip: typeof req.socket?.remoteAddress === "string" ? req.socket.remoteAddress : null,
        ua: typeof req.headers["user-agent"] === "string" ? req.headers["user-agent"] : null,
      };

      const outPath = path.join(__dirname, "contact-submissions.jsonl");
      const line = JSON.stringify(record) + "\n";
      await appendFile(outPath, line, { encoding: "utf8" });

      return send(
        res,
        200,
        { "Content-Type": "application/json; charset=utf-8" },
        JSON.stringify({ ok: true, stored: true }),
      );
    }

    if (pathname === "/og.png") {
      return send(
        res,
        404,
        { "Content-Type": "text/plain; charset=utf-8" },
        "Missing og.png. Add an OpenGraph image at /og.png for production.",
      );
    }

    const fileName = PUBLIC_FILES.get(pathname);
    if (!fileName) {
      return send(res, 404, { "Content-Type": "text/plain; charset=utf-8" }, "Not found");
    }

    const filePath = path.join(__dirname, fileName);
    if (!existsSync(filePath)) {
      return send(res, 404, { "Content-Type": "text/plain; charset=utf-8" }, "File not found");
    }

    const buf = await readFile(filePath);
    const ct = contentTypeFor(fileName);
    return send(res, 200, { "Content-Type": ct, "Cache-Control": "no-store" }, buf);
  } catch {
    return send(res, 500, { "Content-Type": "text/plain; charset=utf-8" }, "Server error");
  }
});

// Ensure sitemap exists with sane defaults on first run.
const sitemapPath = path.join(__dirname, "sitemap.xml");
if (!existsSync(sitemapPath)) {
  const xml =
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    `  <url><loc>https://asset-energy.ai/</loc></url>\n` +
    `</urlset>\n`;
  await writeFile(sitemapPath, xml, "utf8");
}

server.listen(PORT, HOST, () => {
  // eslint-disable-next-line no-console
  console.log(`Landing page running on http://${HOST}:${PORT}`);
});

