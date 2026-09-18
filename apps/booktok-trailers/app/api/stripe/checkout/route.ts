import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@/lib/supabase-server";
import { stripe, PLANS, PlanId } from "@/lib/stripe";
import { env } from "@/lib/env";

export async function POST(req: NextRequest) {
  const { plan } = (await req.json()) as { plan: PlanId };
  if (!PLANS[plan]) return NextResponse.json({ error: "bad plan" }, { status: 400 });

  const supabase = createServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer_email: user.email!,
    line_items: [{ price: PLANS[plan].price, quantity: 1 }],
    success_url: `${env.NEXT_PUBLIC_APP_URL}/dashboard?checkout=success`,
    cancel_url: `${env.NEXT_PUBLIC_APP_URL}/?checkout=cancel`,
    metadata: { user_id: user.id, plan },
    allow_promotion_codes: true,
  });
  return NextResponse.json({ url: session.url });
}
