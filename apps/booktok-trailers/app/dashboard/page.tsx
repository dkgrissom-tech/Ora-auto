import { createServerClient } from "@/lib/supabase-server";

export default async function Dashboard() {
  const supabase = createServerClient();
  const { data: orders } = await supabase
    .from("orders")
    .select("id, amazon_url, status, created_at, generations(preset_id, video_url)")
    .order("created_at", { ascending: false })
    .limit(20);

  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="text-3xl font-semibold">Your trailers</h1>
      <ul className="mt-8 space-y-6">
        {(orders ?? []).map((o) => (
          <li key={o.id} className="rounded-lg border border-neutral-800 p-5">
            <div className="flex items-center justify-between">
              <a href={o.amazon_url} className="truncate text-sm text-neutral-400 hover:underline">
                {o.amazon_url}
              </a>
              <span className="text-xs uppercase tracking-wider text-neutral-500">{o.status}</span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {o.generations?.map((g: { preset_id: string; video_url: string | null }) => (
                <a
                  key={g.preset_id}
                  href={g.video_url ?? "#"}
                  className="block rounded bg-neutral-900 p-3 text-xs hover:bg-neutral-800"
                >
                  {g.preset_id}
                  <br />
                  <span className="text-neutral-500">{g.video_url ? "download" : "pending"}</span>
                </a>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
