import Stripe from "stripe";
import { env } from "./env";

export const stripe = new Stripe(env.STRIPE_SECRET_KEY, { apiVersion: "2025-02-24.acacia" });

export const PLANS = {
  starter: { price: env.STRIPE_PRICE_29, quotaPerWeek: 8, label: "Starter · $29/mo" },
  unlimited: { price: env.STRIPE_PRICE_79, quotaPerWeek: 999, label: "Unlimited · $79/mo" },
} as const;
export type PlanId = keyof typeof PLANS;
