import Link from "next/link";
import { createServerClient } from "@/lib/supabase-server";
import { createServiceClient } from "@/lib/supabase-service";
import { GenerateForm } from "@/app/components/generate-form";
import { SubscribeButton } from "@/app/components/subscribe-button";
import { SignOutButton } from "@/app/components/sign-out-button";
import { PLANS } from "@/lib/stripe";

export default async function Home() {
  const supabase = await createServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  let activePlan: keyof typeof PLANS | null = null;
  if (user) {
    const service = createServiceClient();
    const { data } = await service
      .from("users")
      .select("plan, subscription_status")
      .eq("id", user.id)
      .single();
    if (data?.subscription_status === "active" && data.plan in PLANS) {
      activePlan = data.plan as keyof typeof PLANS;
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <header className="flex items-center justify-between">
        <span className="text-sm font-medium text-neutral-400">BookTok Trailer Factory</span>
        {user ? (
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-sm text-neutral-400 hover:text-white hover:underline">
              Dashboard
            </Link>
            <SignOutButton />
          </div>
        ) : (
          <Link href="/login" className="text-sm text-neutral-400 hover:text-white hover:underline">
            Sign in
          </Link>
        )}
      </header>

      <h1 className="mt-16 text-4xl font-semibold tracking-tight">BookTok Trailer Factory</h1>
      <p className="mt-4 text-lg text-neutral-300">
        Paste any Amazon book URL. Get 8 cinematic vertical trailers in ~6 minutes.
      </p>

      <div className="mt-10">
        {!user && (
          <Link href="/login" className="inline-block rounded-md bg-white px-5 py-3 font-medium text-black">
            Sign in to get started
          </Link>
        )}
        {user && !activePlan && (
          <div className="rounded-lg border border-neutral-800 p-6">
            <p className="text-neutral-300">Subscribe to start generating trailers.</p>
            <div className="mt-4 flex gap-3">
              <SubscribeButton plan="starter" label={PLANS.starter.label} />
              <SubscribeButton plan="unlimited" label={PLANS.unlimited.label} />
            </div>
          </div>
        )}
        {user && activePlan && <GenerateForm />}
      </div>

      <section className="mt-20 grid gap-6 sm:grid-cols-2">
        <div className="rounded-lg border border-neutral-800 p-6">
          <h2 className="text-lg font-medium">{PLANS.starter.label}</h2>
          <p className="mt-2 text-sm text-neutral-400">8 trailers/week</p>
        </div>
        <div className="rounded-lg border border-neutral-800 p-6">
          <h2 className="text-lg font-medium">{PLANS.unlimited.label}</h2>
          <p className="mt-2 text-sm text-neutral-400">Unlimited trailers</p>
        </div>
      </section>
    </main>
  );
}
