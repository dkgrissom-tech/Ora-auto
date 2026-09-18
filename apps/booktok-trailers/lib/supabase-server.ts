import { createServerClient as _createServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers";
import { env } from "./env";

/**
 * Session-aware client for Server Components, Route Handlers and Server Actions.
 * Cookie writes are a no-op when called from a Server Component (Next.js forbids
 * it there) — middleware.ts is what actually refreshes the session cookie.
 */
export async function createServerClient() {
  const cookieStore = await cookies();
  return _createServerClient(env.NEXT_PUBLIC_SUPABASE_URL, env.NEXT_PUBLIC_SUPABASE_ANON_KEY, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll: (cookiesToSet: { name: string; value: string; options: CookieOptions }[]) => {
        try {
          for (const { name, value, options } of cookiesToSet) {
            cookieStore.set(name, value, options);
          }
        } catch {
          // Called from a Server Component render — safe to ignore.
        }
      },
    },
  });
}
