import { Resend } from "resend";
import { env } from "@/lib/env";
import { uploadFile } from "@/lib/s3";
import type { RawClip } from "./generate";
import type { ScrapedBook } from "./scrape";

const resend = new Resend(env.RESEND_API_KEY);

export type Delivered = RawClip & { publicUrl: string };

export async function deliver(args: {
  orderId: string;
  userId: string;
  clips: RawClip[];
  meta: ScrapedBook;
}): Promise<Delivered[]> {
  const uploaded = await Promise.all(
    args.clips.map(async (c) => {
      const key = `orders/${args.orderId}/${c.presetId}.mp4`;
      const publicUrl = await uploadFile(c.localPath, key);
      return { ...c, publicUrl };
    }),
  );

  const listHtml = uploaded
    .map((c) => `<li><a href="${c.publicUrl}">${c.presetId}.mp4</a></li>`)
    .join("");

  await resend.emails.send({
    from: env.RESEND_FROM,
    to: (await getUserEmail(args.userId)) ?? "",
    subject: `Your 8 BookTok trailers for "${args.meta.title}"`,
    html: `
      <h2>Your trailers are ready</h2>
      <p><strong>${args.meta.title}</strong> — ${args.meta.author}</p>
      <ul>${listHtml}</ul>
      <p>Dashboard: <a href="${env.NEXT_PUBLIC_APP_URL}/dashboard">${env.NEXT_PUBLIC_APP_URL}/dashboard</a></p>
    `,
  });

  return uploaded;
}

async function getUserEmail(userId: string): Promise<string | null> {
  const { createServiceClient } = await import("@/lib/supabase-server");
  const service = createServiceClient();
  const { data } = await service.auth.admin.getUserById(userId);
  return data.user?.email ?? null;
}
