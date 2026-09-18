import { CAMERA_PRESETS } from "@/lib/presets";
import { higgsfieldImageToVideo } from "@/lib/higgsfield";
import { runComfyWorkflow } from "@/lib/comfyui";
import { env } from "@/lib/env";
import { join } from "node:path";
import { writeFile } from "node:fs/promises";

export type RawClip = { presetId: string; localPath: string; sourceUrl: string };

async function download(url: string, dest: string): Promise<void> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`download ${url} → ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  await writeFile(dest, buf);
}

export async function generateTrailers(args: {
  workdir: string;
  cover: string;
  blurb: string;
}): Promise<RawClip[]> {
  const { workdir, cover, blurb } = args;
  const hybridEnabled = !!env.COMFYUI_ENDPOINT && env.COMFYUI_LOCAL_FRACTION > 0;

  return Promise.all(
    CAMERA_PRESETS.map(async (preset, i) => {
      const prompt = `${blurb.slice(0, 200)}. ${preset.prompt_suffix}`;
      const useLocal = hybridEnabled && i / CAMERA_PRESETS.length < env.COMFYUI_LOCAL_FRACTION;

      const { url } = useLocal
        ? await runComfyWorkflow({
            workflowPath: join(process.cwd(), "worker", "workflows", `wan22_${preset.id}.json`),
            imagePath: cover,
            prompt,
          })
        : await higgsfieldImageToVideo({
            startImagePath: cover,
            prompt,
            durationSeconds: 5,
            aspectRatio: "9:16",
          });

      const localPath = join(workdir, `${preset.id}.mp4`);
      await download(url, localPath);
      return { presetId: preset.id, localPath, sourceUrl: url };
    }),
  );
}
