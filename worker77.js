export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const { pathname, searchParams } = url;

    // صفحه لاگین
    if (pathname === "/login") {
      if (request.method === "POST") {
        const formData = await request.formData();
        const pass = formData.get("password");
        const realPass = await env.SUBS.get("PANEL_PASS");

        if (pass === realPass) {
          const res = new Response("", { status: 302 });
          res.headers.set("Location", "/panel");
          res.headers.set("Set-Cookie", `auth=${realPass}; path=/; HttpOnly`);
          return res;
        } else {
          return new Response(renderLogin("❌ رمز اشتباه است"), {
            headers: { "Content-Type": "text/html;charset=UTF-8" },
          });
        }
      }
      return new Response(renderLogin(), {
        headers: { "Content-Type": "text/html;charset=UTF-8" },
      });
    }

    // صفحه پنل اصلی فقط در صورت لاگین
    if (pathname === "/panel") {
      const cookie = request.headers.get("Cookie") || "";
      const auth = cookie.split(";").find(c => c.trim().startsWith("auth="));
      const value = auth ? auth.split("=")[1] : null;
      const realPass = await env.SUBS.get("PANEL_PASS");

      if (value !== realPass) {
        return Response.redirect("/login", 302);
      }
      return new Response(renderPanel(), {
        headers: { "Content-Type": "text/html;charset=UTF-8" },
      });
    }

    // دیفالت -> ری‌دایرکت به لاگین
    return Response.redirect("/login", 302);
  },
};

// صفحه لاگین شیک
function renderLogin(msg = "") {
  return `
<!DOCTYPE html>
<html lang="fa">
<head>
  <meta charset="UTF-8" />
  <title>ورود پنل</title>
  <style>
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background: linear-gradient(135deg,#2c3e50,#3498db);
      font-family: Vazirmatn, sans-serif;
      color: white;
    }
    .box {
      background: rgba(0,0,0,0.4);
      padding: 30px;
      border-radius: 16px;
      text-align: center;
      width: 320px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    }
    input {
      width: 90%;
      padding: 10px;
      border-radius: 8px;
      border: none;
      margin-top: 10px;
      font-size: 16px;
      text-align: center;
    }
    button {
      margin-top: 15px;
      padding: 10px 20px;
      background: #27ae60;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
    }
    h1 {
      font-size: 22px;
      margin-bottom: 10px;
    }
    .msg {
      color: #ff7675;
      margin-top: 10px;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="box">
    <h1>⚡ ورود به پنل ⚡</h1>
    <form method="POST">
      <input type="password" name="password" placeholder="رمز عبور را وارد کنید" required />
      <br/>
      <button type="submit">ورود</button>
    </form>
    ${msg ? `<div class="msg">${msg}</div>` : ""}
  </div>
</body>
</html>`;
}

// اینجا پنل اصلی شیکت میاد 👇
// کل کد پنل قبلی (همونی که الان داری و خیلی خوشت اومده)
// فقط کافی جای متن پایین کل HTML قبلیتو بذاری
function renderPanel() {
  return `
<!DOCTYPE html>
<html lang="fa">
<head>
  <meta charset="UTF-8" />
  <title>⚡ My Semi-Pro Panel ⚡</title>
  <style>
    body {
      font-family: Vazirmatn, sans-serif;
      background: #1e272e;
      color: #f5f6fa;
      padding: 20px;
    }
    h1 { color: #0fbcf9; }
    .card {
      background: #2f3640;
      border-radius: 16px;
      padding: 20px;
      margin: 20px auto;
      max-width: 800px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>⚡ My Semi-Pro Panel ⚡</h1>
    <p>📡 مدیریت سورس‌ها و ساخت Sub</p>
    <p>🎛 پیکربندی و تنظیمات دلخواه</p>
    <!-- 👇 اینجا همون سورس و خروجی‌هایی که داشتی بیاد -->
  </div>
</body>
</html>
  `;
}
