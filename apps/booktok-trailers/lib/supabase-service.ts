import { createClient } from "@supabase/supabase-js";
import { env } from "./env";

/**
 * Service-role client: bypasses RLS, no user session or cookies involved.
 * Safe from Next.js route handlers AND the standalone worker process — unlike
 * lib/supabase-server.ts, this never touches next/headers.
 */
export function createServiceClient() {
  return createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
