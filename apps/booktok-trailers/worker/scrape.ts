import { chromium } from "playwright";
import { writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

export type ScrapedBook = {
  title: string;
  author: string;
  blurb: string;
  hook: string;
  coverPath: string;
};

export async function scrapeAmazon(url: string, workdir: string): Promise<ScrapedBook> {
  await mkdir(workdir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15" });
  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });

    const title = (await page.locator("#productTitle").innerText().catch(() => "Untitled")).trim();
    const author = (await page.locator("#bylineInfo .author a").first().innerText().catch(() => "")).trim();
    const blurb = (await page.locator("#bookDescription_feature_div").innerText().catch(() => "")).trim().slice(0, 600) || title;
    const coverUrl = await page.locator("#landingImage").getAttribute("src");
    if (!coverUrl) throw new Error("cover image not found on Amazon page");

    const coverBuf = await page.request.get(coverUrl).then((r) => r.body());
    const coverPath = join(workdir, "cover.jpg");
    await writeFile(coverPath, coverBuf);

    // 55-char hook = first sentence, trimmed. Fallback: title.
    const hook = (blurb.split(/(?<=[.!?])\s+/)[0] ?? title).slice(0, 55);

    return { title, author, blurb, hook, coverPath };
  } finally {
    await browser.close();
  }
}
