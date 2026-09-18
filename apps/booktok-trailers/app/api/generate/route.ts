import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { createServerClient, createServiceClient } from "@/lib/supabase-server";
import { trailerQueue } from "@/lib/queue";

const Body = z.object({
  amazonUrl: z.string().url().refine((u) => /amazon\./.test(u), "Must be an Amazon URL"),
});

export async function POST(req: NextRequest) {
  const parsed = Body.safeParse(await req.json().catch(() => ({})));
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const supabase = createServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  // Quota check
  const service = createServiceClient();
  const { data: usage } = await service.rpc("weekly_usage", { p_user_id: user.id });
  const { data: plan } = await service.from("users").select("plan, quota_per_week").eq("id", user.id).single();
  if (plan && usage && usage >= plan.quota_per_week) {
    return NextResponse.json({ error: "quota exceeded for this week" }, { status: 402 });
  }

  const { data: order, error } = await service
    .from("orders")
    .insert({ user_id: user.id, amazon_url: parsed.data.amazonUrl, status: "queued" })
    .select("id")
    .single();
  if (error || !order) return NextResponse.json({ error: error?.message ?? "insert failed" }, { status: 500 });

  await trailerQueue.add(
    "trailer",
    { orderId: order.id, userId: user.id, amazonUrl: parsed.data.amazonUrl },
    { attempts: 2, backoff: { type: "exponential", delay: 30_000 } },
  );

  return NextResponse.json({ id: order.id });
}
