import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { env } from "./env";

const run = promisify(execFile);

/**
 * Runs the Higgsfield CLI: `higgsfield generate create <model> ... --wait --json`
 * Requires `higgsfield auth login` to have been completed on the worker host.
 */
export async function higgsfieldImageToVideo(args: {
  startImagePath: string;
  prompt: string;
  durationSeconds?: number;
  aspectRatio?: "9:16" | "16:9" | "1:1";
  model?: string;
}): Promise<{ url: string; job_id: string; raw: unknown }> {
  const {
    startImagePath,
    prompt,
    durationSeconds = 5,
    aspectRatio = "9:16",
    model = env.HIGGSFIELD_VIDEO_MODEL,
  } = args;

  const { stdout } = await run(
    "higgsfield",
    [
      "generate",
      "create",
      model,
      "--prompt",
      prompt,
      "--start-image",
      startImagePath,
      "--duration",
      String(durationSeconds),
      "--aspect-ratio",
      aspectRatio,
      "--mode",
      "pro",
      "--sound",
      "off",
      "--wait",
      "--json",
    ],
    { maxBuffer: 20 * 1024 * 1024 },
  );

  const parsed = JSON.parse(stdout) as {
    id?: string;
    job_id?: string;
    url?: string;
    video_url?: string;
    output?: { url?: string };
  };
  const url = parsed.url ?? parsed.video_url ?? parsed.output?.url;
  const job_id = parsed.id ?? parsed.job_id ?? "";
  if (!url) throw new Error(`higgsfield CLI returned no url: ${stdout.slice(0, 400)}`);
  return { url, job_id, raw: parsed };
}
