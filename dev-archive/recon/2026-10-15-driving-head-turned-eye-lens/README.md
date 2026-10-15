# 2026-10-15 late evening: driving with the head turned, the eye-lens fix, the camera line

Dev PC, `/lm`, OpenXR simulator, builds `2a5ce5e5eda5` (drive runs) and `eb6f5ccee224` (camera line, eye lens).
Write-up: `modding-notes/2026-10-15-lm-driving-head-turned-and-the-eye-lens.md`.

| file | what |
| --- | --- |
| `sim-drive-yaw20-left-ground-missing.jpg` | driving straight, head 20 deg left: blue strip on the left |
| `sim-drive-yaw20-right-ground-missing-shadow-slabs.jpg` | driving and turning, head 20 deg right: dark slabs and blue on the right |
| `game-drive-yaw20-right.png` | the game window at the same moment: the ground missing on the right |
| `sim-drive-yaw0-clean.jpg` | control, head straight while driving: clean |
| `sim-cockpit-driving-yaw0.jpg`, `sim-cockpit-driving-yaw30.jpg` | the cockpit view while driving, 3D at 0.065 |
| `sim-eyelens80-game117-yaw15-whole.jpg` | `eye_hfov=80`, game at 116.9 deg, head 15 deg: the ground whole |
| `sim-eyelens80-game117-yaw30-gap-back.jpg` | the same at 30 deg, beyond the 18 deg covered: the gap back |
| `sim-eyelens80-drive-yaw15-whole.jpg` | the same, driving with the head 15 deg right: whole |
| `key-log-lines.txt` | the runtime name, the eye-lens line, the game's field of view (`shared_w`) |
