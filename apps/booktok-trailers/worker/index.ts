import "./load-env";
import { Worker } from "bullmq";
import IORedis from "ioredis";
import { env } from "@/lib/env";
import { createServiceClient } from "@/lib/supabase-service";
import { scrapeAmazon } from "./scrape";
import { generateTrailers } from "./generate";
import { captionAll } from "./caption";
import { deliver } from "./deliver";
import { rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { TrailerJob } from "@/lib/queue";

const connection = new IORedis(env.REDIS_URL, { maxRetriesPerRequest: null });
const service = createServiceClient();

new Worker<TrailerJob>(
  "trailer-jobs",
  async (job) => {
    const { orderId, userId, amazonUrl } = job.data;
    const workdir = join(tmpdir(), `booktok-${orderId}`);
    console.log(`[${orderId}] start (${amazonUrl})`);

    try {
      await service.from("orders").update({ status: "scraping" }).eq("id", orderId);
      const meta = await scrapeAmazon(amazonUrl, workdir);

      await service.from("orders").update({ status: "generating", title: meta.title, author: meta.author }).eq("id", orderId);
      const raw = await generateTrailers({ workdir, cover: meta.coverPath, blurb: meta.blurb });

      await service.from("orders").update({ status: "captioning" }).eq("id", orderId);
      const captioned = await captionAll({ workdir, clips: raw, hook: meta.hook });

      await service.from("orders").update({ status: "delivering" }).eq("id", orderId);
      const delivered = await deliver({ orderId, userId, clips: captioned, meta });

      // Persist per-preset rows
      for (const c of delivered) {
        await service.from("generations").insert({
          order_id: orderId,
          preset_id: c.presetId,
          video_url: c.publicUrl,
        });
      }
      await service.from("orders").update({ status: "done" }).eq("id", orderId);
      console.log(`[${orderId}] done — ${delivered.length} trailers`);
    } catch (err) {
      const msg = (err as Error).message;
      console.error(`[${orderId}] failed:`, msg);
      await service.from("orders").update({ status: "failed", error: msg }).eq("id", orderId);
      throw err;
    } finally {
      await rm(workdir, { recursive: true, force: true }).catch(() => {});
    }
  },
  { connection, concurrency: 2 },
);

console.log("worker running");
