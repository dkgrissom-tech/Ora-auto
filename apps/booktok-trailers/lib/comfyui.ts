import { readFile } from "node:fs/promises";
import { env } from "./env";

/**
 * Phase 2 hybrid inference. Feature-flagged by COMFYUI_ENDPOINT.
 * Loads an API-format ComfyUI graph, injects prompt + image, submits, polls history.
 *
 * Node id assumptions (edit to match your graph):
 *   "6"  → CLIPTextEncode (positive prompt)
 *   "14" → LoadImage
 *   "9"  → SaveVideo (output collection)
 */
export async function runComfyWorkflow(args: {
  workflowPath: string;
  imagePath: string;
  prompt: string;
  pollMs?: number;
  timeoutMs?: number;
}): Promise<{ url: string }> {
  if (!env.COMFYUI_ENDPOINT) throw new Error("COMFYUI_ENDPOINT not set (Phase 2 not enabled)");

  const { workflowPath, imagePath, prompt, pollMs = 2000, timeoutMs = 15 * 60_000 } = args;
  const workflow = JSON.parse(await readFile(workflowPath, "utf8"));
  workflow["6"].inputs.text = prompt;
  workflow["14"].inputs.image = imagePath;

  const submit = await fetch(`${env.COMFYUI_ENDPOINT}/prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: workflow }),
  });
  if (!submit.ok) throw new Error(`ComfyUI submit failed: ${submit.status}`);
  const { prompt_id } = (await submit.json()) as { prompt_id: string };

  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const h = await fetch(`${env.COMFYUI_ENDPOINT}/history/${prompt_id}`).then((r) => r.json());
    const entry = (h as Record<string, { status?: { completed?: boolean }; outputs?: Record<string, { videos?: Array<{ filename: string; subfolder: string; type: string }> }> }>)[prompt_id];
    if (entry?.status?.completed) {
      const out = entry.outputs?.["9"]?.videos?.[0];
      if (!out) throw new Error("ComfyUI completed but no video output at node 9");
      return {
        url: `${env.COMFYUI_ENDPOINT}/view?filename=${out.filename}&subfolder=${out.subfolder}&type=${out.type}`,
      };
    }
    await new Promise((r) => setTimeout(r, pollMs));
  }
  throw new Error("ComfyUI job timed out");
}
