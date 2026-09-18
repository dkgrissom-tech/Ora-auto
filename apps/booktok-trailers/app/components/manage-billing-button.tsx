"use client";

import { useState } from "react";

export function ManageBillingButton() {
  const [loading, setLoading] = useState(false);

  async function go() {
    setLoading(true);
    try {
      const res = await fetch("/api/stripe/portal", { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const { url } = await res.json();
      window.location.href = url;
    } catch {
      setLoading(false);
    }
  }

  return (
    <button onClick={go} disabled={loading} className="text-sm text-neutral-400 hover:text-white hover:underline">
      {loading ? "Loading…" : "Manage billing"}
    </button>
  );
}
