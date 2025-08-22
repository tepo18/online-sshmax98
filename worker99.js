export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // --- صفحه لاگین ---
    if (url.pathname === "/login") {
      return new Response(`
        <html>
          <head>
            <title>⚡ ورود به پنل ⚡</title>
            <style>
              body {
                background: linear-gradient(135deg, #1f1c2c, #928dab);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                color: white;
              }
              .login-box {
                background: rgba(0,0,0,0.6);
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
              }
              input {
                padding: 10px;
                margin: 10px 0;
                border: none;
                border-radius: 5px;
                width: 200px;
              }
              button {
                padding: 10px 20px;
                background: #4cafef;
                border: none;
                border-radius: 5px;
                color: white;
                cursor: pointer;
                font-weight: bold;
              }
              h2 { margin-bottom: 20px; }
            </style>
          </head>
          <body>
            <div class="login-box">
              <h2>🔑 رمز ورود پنل</h2>
              <form method="POST" action="/auth">
                <input type="password" name="pass" placeholder="رمز عبور" required>
                <br>
                <button type="submit">ورود</button>
              </form>
            </div>
          </body>
        </html>
      `, { headers: { "content-type": "text/html;charset=UTF-8" } });
    }

    // --- بررسی رمز ---
    if (url.pathname === "/auth" && request.method === "POST") {
      const form = await request.formData();
      const pass = form.get("pass");
      const realPass = await env.SUBS.get("PANEL_PASS"); // رمزتو توی KV بذار: PANEL_PASS
      if (pass === realPass) {
        // موفق → هدایت به پنل
        return Response.redirect("/panel", 302);
      } else {
        return new Response("❌ رمز اشتباهه!", { status: 403 });
      }
    }

    // --- اگر لاگین نکرده، بفرست لاگین ---
    if (url.pathname === "/" || url.pathname === "/panel") {
      // اگه هنوز لاگین نکرده
      if (request.headers.get("cookie") !== "ok") {
        return Response.redirect("/login", 302);
      }
    }

    // --- اینجا همون پنل شیک اصلیت ---
    if (url.pathname === "/panel") {
      return new Response(`
        <html>
          <head>
            <meta charset="utf-8" />
            <title>⚡ My Semi-Pro Panel ⚡</title>
            <style>
              body {
                background: linear-gradient(135deg, #2c3e50, #4ca1af);
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: white;
              }
              header {
                padding: 15px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                background: rgba(0,0,0,0.3);
              }
              .container {
                padding: 30px;
                max-width: 900px;
                margin: auto;
              }
              .card {
                background: rgba(0,0,0,0.5);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.4);
              }
              h3 { margin-top: 0; }
              a {
                color: #ffd700;
                text-decoration: none;
                font-weight: bold;
              }
            </style>
          </head>
          <body>
            <header>⚡ My Semi-Pro Panel ⚡</header>
            <div class="container">
              <div class="card">
                <h3>📡 مدیریت سورس‌ها و ساخت Sub</h3>
                <p>اینجا لیست سورس‌ها و خروجی‌هایت را مدیریت کن.</p>
              </div>
              <div class="card">
                <h3>🎛 پیکربندی و تنظیمات دلخواه</h3>
                <p>پروتکل‌ها، خروجی‌ها و نوع Sub را اینجا تنظیم کن.</p>
              </div>
            </div>
          </body>
        </html>
      `, { headers: { "content-type": "text/html;charset=UTF-8" } });
    }

    // پیش‌فرض
    return new Response("Not Found", { status: 404 });
  }
}
