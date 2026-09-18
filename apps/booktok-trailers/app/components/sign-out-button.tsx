"use client";

import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase-browser";

export function SignOutButton() {
  const router = useRouter();

  async function signOut() {
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  }

  return (
    <button onClick={signOut} className="text-sm text-neutral-400 hover:text-white hover:underline">
      Sign out
    </button>
  );
}
