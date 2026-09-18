import { NextRequest, NextResponse } from "next/server";
import { stripe, PLANS, PlanId } from "@/lib/stripe";
import { createServiceClient } from "@/lib/supabase-service";
import { env } from "@/lib/env";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const sig = req.headers.get("stripe-signature");
  if (!sig) return NextResponse.json({ error: "missing signature" }, { status: 400 });
  const buf = Buffer.from(await req.arrayBuffer());
  let event;
  try {
    event = stripe.webhooks.constructEvent(buf, sig, env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return NextResponse.json({ error: (err as Error).message }, { status: 400 });
  }

  const service = createServiceClient();

  if (event.type === "checkout.session.completed") {
    const s = event.data.object as { metadata?: { user_id?: string; plan?: PlanId }; customer?: string; subscription?: string };
    const userId = s.metadata?.user_id;
    const plan = (s.metadata?.plan ?? "starter") as PlanId;
    if (userId) {
      await service.from("users").update({
        stripe_customer_id: s.customer,
        stripe_subscription_id: s.subscription,
        plan,
        quota_per_week: PLANS[plan].quotaPerWeek,
        subscription_status: "active",
      }).eq("id", userId);
    }
  }

  if (event.type === "customer.subscription.deleted") {
    const sub = event.data.object as { customer?: string };
    await service.from("users").update({ subscription_status: "canceled", quota_per_week: 0 })
      .eq("stripe_customer_id", sub.customer ?? "");
  }

  return NextResponse.json({ received: true });
}
