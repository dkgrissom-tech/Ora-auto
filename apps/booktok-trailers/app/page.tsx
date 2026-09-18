"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amazonUrl: url }),
      });
      if (!res.ok) throw new Error(await res.text());
      const { id } = await res.json();
      setJobId(id);
      setStatus("done");
    } catch (err) {
      setError((err as Error).message);
      setStatus("error");
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-24">
      <h1 className="text-4xl font-semibold tracking-tight">BookTok Trailer Factory</h1>
      <p className="mt-4 text-lg text-neutral-300">
        Paste any Amazon book URL. Get 8 cinematic vertical trailers in ~6 minutes.
      </p>

      <form onSubmit={submit} className="mt-10 flex gap-3">
        <input
          type="url"
          required
          placeholder="https://www.amazon.com/dp/..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="flex-1 rounded-md border border-neutral-700 bg-neutral-900 px-4 py-3"
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="rounded-md bg-white px-5 py-3 font-medium text-black disabled:opacity-50"
        >
          {status === "loading" ? "Queuing…" : "Generate 8 trailers"}
        </button>
      </form>

      {jobId && (
        <p className="mt-6 text-sm text-neutral-400">
          Job queued: <code>{jobId}</code>. Track it at{" "}
          <a className="underline" href={`/dashboard`}>your dashboard</a>.
        </p>
      )}
      {error && <p className="mt-6 text-sm text-red-400">Error: {error}</p>}
    </main>
  );
}
