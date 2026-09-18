import { Queue } from "bullmq";
import IORedis from "ioredis";
import { env } from "./env";

const connection = new IORedis(env.REDIS_URL, { maxRetriesPerRequest: null });

export type TrailerJob = {
  orderId: string;
  userId: string;
  amazonUrl: string;
};

export const trailerQueue = new Queue<TrailerJob>("trailer-jobs", { connection });
