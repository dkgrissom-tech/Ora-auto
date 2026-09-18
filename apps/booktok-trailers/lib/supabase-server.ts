import { createServerClient as _create } from "@supabase/ssr";
import { cookies } from "next/headers";
import { env } from "./env";

export function createServerClient() {
  const cookieStore = cookies();
  return _create(env.NEXT_PUBLIC_SUPABASE_URL, env.NEXT_PUBLIC_SUPABASE_ANON_KEY, {
    cookies: {
      get: (name) => cookieStore.get(name)?.value,
      set: () => {},
      remove: () => {},
    },
  });
}

export function createServiceClient() {
  return _create(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
    cookies: { get: () => undefined, set: () => {}, remove: () => {} },
  });
}
