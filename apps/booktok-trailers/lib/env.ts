import { z } from "zod";

const schema = z.object({
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
  STRIPE_SECRET_KEY: z.string().min(1),
  STRIPE_WEBHOOK_SECRET: z.string().min(1),
  STRIPE_PRICE_29: z.string().min(1),
  STRIPE_PRICE_79: z.string().min(1),
  REDIS_URL: z.string().min(1),
  AWS_REGION: z.string().default("us-east-1"),
  AWS_ACCESS_KEY_ID: z.string().min(1),
  AWS_SECRET_ACCESS_KEY: z.string().min(1),
  S3_BUCKET: z.string().min(1),
  S3_PUBLIC_BASE_URL: z.string().url(),
  RESEND_API_KEY: z.string().min(1),
  RESEND_FROM: z.string().min(1),
  HIGGSFIELD_VIDEO_MODEL: z.string().default("kling3_0"),
  COMFYUI_ENDPOINT: z.string().default(""),
  COMFYUI_LOCAL_FRACTION: z.coerce.number().min(0).max(1).default(0),
});

export const env = schema.parse(process.env);
export type Env = z.infer<typeof schema>;
