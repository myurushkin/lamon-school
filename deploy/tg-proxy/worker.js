// Cloudflare Worker: прокси к Telegram Bot API для сервера, с которого api.telegram.org недоступен.
// Секрет PROXY_KEY задаётся в настройках Worker (Settings → Variables and Secrets).
export default {
  async fetch(req, env) {
    if (req.headers.get("x-proxy-key") !== env.PROXY_KEY) return new Response("forbidden", { status: 403 });
    const u = new URL(req.url);
    if (!u.pathname.startsWith("/bot")) return new Response("not found", { status: 404 });
    const init = { method: req.method, headers: { "content-type": req.headers.get("content-type") || "application/x-www-form-urlencoded" } };
    if (req.method === "POST") init.body = await req.arrayBuffer();
    const r = await fetch("https://api.telegram.org" + u.pathname + u.search, init);
    return new Response(r.body, { status: r.status, headers: { "content-type": r.headers.get("content-type") || "application/json" } });
  },
};
