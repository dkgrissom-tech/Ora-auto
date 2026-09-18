import { config } from "dotenv";

// The worker runs standalone via tsx, not through Next.js, so it needs its
// own .env.local loading — dotenv/config alone would default to ./.env.
config({ path: ".env.local" });
