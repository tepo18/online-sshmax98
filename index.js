export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 🔑 رمز ورود
    const PANEL_PASSWORD = "15601560";

    // مسیر ورود به پنل
    if (url.pathname === "/login" && request.method === "POST") {
      const formData = await request.formData();
      const password = formData.get("password");
      if (password === PANEL_PASSWORD) {
        return new Response("✅ Login successful. Welcome to tak30 Panel!", {
          headers: { "content-type": "text/plain" },
        });
      } else {
        return new Response("❌ Wrong password!", { status: 401 });
      }
    }

    // صفحه اصلی (فرم لاگین)
    if (url.pathname === "/") {
      return new Response(`
        <!DOCTYPE html>
        <html lang="fa">
        <head>
          <meta charset="UTF-8" />
          <title>پنل tak30</title>
          <style>
            body { font-family: sans-serif; background:#0d1117; color:#f0f6fc; text-align:center; padding:50px; }
            form { background:#161b22; padding:20px; border-radius:12px; display:inline-block; }
            input { padding:10px; margin:5px; border-radius:8px; border:1px solid #30363d; background:#0d1117; color:#f0f6fc; }
            button { padding:10px 20px; background:#238636; border:none; border-radius:8px; color:white; cursor:pointer; }
          </style>
        </head>
        <body>
          <h1>🔑 ورود به پنل tak30</h1>
          <form method="POST" action="/login">
            <input type="password" name="password" placeholder="رمز عبور" required />
            <br />
            <button type="submit">ورود</button>
          </form>
        </body>
        </html>
      `, {
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    }

    return new Response("Not Found", { status: 404 });
  }
}
