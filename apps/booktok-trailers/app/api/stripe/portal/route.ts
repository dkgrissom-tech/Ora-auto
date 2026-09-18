import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@/lib/supabase-server";
import { createServiceClient } from "@/lib/supabase-service";
import { stripe } from "@/lib/stripe";
import { env } from "@/lib/env";

export async function POST(_req: NextRequest) {
  const supabase = await createServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const service = createServiceClient();
  const { data: row } = await service
    .from("users")
    .select("stripe_customer_id")
    .eq("id", user.id)
    .single();
  if (!row?.stripe_customer_id) {
    return NextResponse.json({ error: "no billing account yet — subscribe first" }, { status: 400 });
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: row.stripe_customer_id,
    return_url: `${env.NEXT_PUBLIC_APP_URL}/dashboard`,
  });
  return NextResponse.json({ url: session.url });
}
