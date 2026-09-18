import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { join } from "node:path";
import type { RawClip } from "./generate";

const run = promisify(execFile);

export async function captionAll(args: { workdir: string; clips: RawClip[]; hook: string }) {
  const { workdir, clips, hook } = args;
  const safe = hook.replace(/'/g, "\u2019").replace(/:/g, ";");

  return Promise.all(
    clips.map(async (c) => {
      const out = join(workdir, `${c.presetId}_captioned.mp4`);
      // drawtext with a semi-transparent black bar background at the top third
      const filter =
        `drawbox=y=(h/3)-70:width=iw:height=140:color=black@0.55:t=fill,` +
        `drawtext=fontfile=/System/Library/Fonts/Supplemental/Impact.ttf:` +
        `text='${safe}':fontcolor=white:fontsize=54:x=(w-tw)/2:y=(h/3)-45:` +
        `borderw=2:bordercolor=black@0.8`;
      await run("ffmpeg", ["-y", "-i", c.localPath, "-vf", filter, "-c:a", "copy", out], {
        maxBuffer: 100 * 1024 * 1024,
      });
      return { ...c, localPath: out };
    }),
  );
}
