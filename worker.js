export default {
  async fetch(request) {
    const url = new URL(request.url);
    const fileName = url.searchParams.get("file");

    // لاگ ساده (برای Debug در بخش Workers Logs)
    console.log("Received file param:", fileName);

    if (!fileName) {
      return new Response(
        "برای دریافت فایل، از پارامتر ?file=filename استفاده کنید\nمثال: ?file=config.json",
        { status: 400 }
      );
    }

    const githubUsername = "tepo18"; // نام کاربری گیت‌هاب
    const repoName = "reza-shah130"; // نام ریپو
    const branch = "main"; // شاخه

    const githubRawUrl = `https://raw.githubusercontent.com/${githubUsername}/${repoName}/${branch}/${fileName}`;

    try {
      const githubResponse = await fetch(githubRawUrl);
      if (!githubResponse.ok) {
        return new Response("فایل پیدا نشد", { status: 404 });
      }
      const content = await githubResponse.text();
      return new Response(content, { status: 200 });
    } catch (error) {
      return new Response("خطا در دریافت فایل", { status: 500 });
    }
  },
};
