export type CameraPreset = {
  id: string;
  label: string;
  prompt_suffix: string;
};

export const CAMERA_PRESETS: CameraPreset[] = [
  {
    id: "push-in",
    label: "Slow Push-In",
    prompt_suffix:
      "slow cinematic push-in on cover, romantic film grain, subtle candlelight glow, shallow depth of field",
  },
  {
    id: "orbit",
    label: "180° Orbit",
    prompt_suffix:
      "smooth 180-degree orbit around subject, shallow depth of field, moody atmospheric lighting",
  },
  {
    id: "dolly-in",
    label: "Dolly-In",
    prompt_suffix:
      "steady dolly-in through the scene, anamorphic bokeh, cinematic teal-and-orange grade",
  },
  {
    id: "crane-up",
    label: "Crane Reveal",
    prompt_suffix:
      "slow crane-up revealing wider environment, golden hour, dust motes floating in the air",
  },
  {
    id: "fpv-drone",
    label: "FPV Drone",
    prompt_suffix:
      "FPV drone fly-through, sweeping motion, high energy trailer feel, dynamic reframing",
  },
  {
    id: "pan-right",
    label: "Slow Pan",
    prompt_suffix:
      "slow horizontal pan right across the scene, film grain, contemplative pacing",
  },
  {
    id: "zoom-out",
    label: "Zoom Out",
    prompt_suffix:
      "dramatic zoom-out reveal, wide vista, epic scale, dust and haze in the atmosphere",
  },
  {
    id: "handheld",
    label: "Handheld Tension",
    prompt_suffix:
      "handheld tension, subtle shake, thriller-style urgency, high contrast lighting",
  },
];
