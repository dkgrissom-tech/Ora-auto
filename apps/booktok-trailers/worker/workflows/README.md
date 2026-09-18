# Phase 2 — ComfyUI Workflow Files

Empty for now. Populate when Idea 1 hits 40+ paying users and you're ready to swap inference to your own GPU.

## What goes here

One API-format JSON graph per camera preset:

```
wan22_push-in.json
wan22_orbit.json
wan22_dolly-in.json
wan22_crane-up.json
wan22_fpv-drone.json
wan22_pan-right.json
wan22_zoom-out.json
wan22_handheld.json
```

## How to export a workflow

1. In ComfyUI, build a Wan 2.2 image-to-video graph with `Wan2.2-Fun-Camera-Control-14B` as the camera-conditioning node.
2. Set the CLIPTextEncode positive-prompt node id to `6` (or update `lib/comfyui.ts`).
3. Set the LoadImage node id to `14`.
4. Set the SaveVideo (or VHS_VideoCombine) node id to `9`.
5. Settings → Enable Dev Mode Options.
6. File menu → **Save (API Format)** → save into this directory with the name above.

## How the worker chooses local vs. API

Set `COMFYUI_ENDPOINT` and `COMFYUI_LOCAL_FRACTION` in `.env.local`:

- `COMFYUI_LOCAL_FRACTION=0` — 100% Higgsfield API (Phase 1 default)
- `COMFYUI_LOCAL_FRACTION=0.5` — first half of presets go local, second half via API (soft launch)
- `COMFYUI_LOCAL_FRACTION=1` — 100% local, API only for failover
