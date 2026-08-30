# A mature, AOB-based Cheat Engine table already documents extensive camera/FOV/function-call access

**Status:** 🆕 new · **Priority:** high — the most concrete, actionable prior art found so far for
`ENGINE-DOSSIER.md` §6 (camera & projection) and potentially §9/§10 (cvar-equivalent control, harness
recipe).

## What it is

The **FearLess Cheat Engine** community forum (fearlessrevolution.com — a long-established,
legitimate Cheat Engine table-sharing community; Cheat Engine itself is a widely-used, legal
memory-scanning/editing tool for single-player games, not a piracy or DRM-circumvention tool) hosts
a **"Mad Max 1.03 AOB Cheat Table"** covering both GOG and Steam builds. AOB ("array of bytes")
signature scanning means the table finds its targets by scanning for a distinctive instruction/byte
pattern near the code that reads/writes each value, rather than a hardcoded static address — a
technique that survives game updates far better than raw offsets, and one this project's own tooling
should consider using the same way once live memory work starts.

Per the thread's own feature list, this single table already includes:

- **Photo Mode camera range control**
- **FOV control**
- **Custom aspect ratio control**
- **HUD removal** (separate toggles for in-game vs. Photo Mode)
- **Screen-effects toggle** and **distant depth-of-field removal**
- Multiple **camera behavior controls**: zoom while driving, a "wasteland exploration" narrow-zoom
  mode, zoom-out while driving, freeze cam, rearview cam, and other positioning options
- **Timeflow control** (time-of-day/weather pacing)
- A **function call handler** — described as being able to directly invoke specific game functions
  (change weather, call storms, spawn cars, **change camera**, run other cheats)

## Why this matters enormously for this project

1. **Someone has already located, and made externally callable, a "change camera" game function.**
   That's not just a memory-read of camera state — it implies they found an actual function pointer/
   address for camera-mode switching, which is a substantial reverse-engineering result directly
   relevant to `ENGINE-DOSSIER.md` §6's core question (how the camera system is driven, not just
   where its output lives).
2. **FOV, aspect ratio, and camera-range control together suggest the projection parameters aren't
   buried deep or scattered** — a working, comprehensive Cheat Engine table implies these values are
   reachable via ordinary memory scanning (no unusual obfuscation defeating that class of tool),
   which is a good sign for this project's own live-memory investigation, independent of whatever
   hooking/proxy-DLL approach is chosen for the actual mod.
3. **This is corroborating, independent confirmation of the vorpX and native-Capture-Mode findings**
   (companion topics from the previous sweep) — three separate, independent sources have now all
   found the camera/FOV system tractable on this exact game.

## Caveats

- This research pass could not open or inspect the actual `.CT` file (Cheat Engine table) content —
  only the thread's own text description of its features, which is what's summarized above. No
  specific memory addresses, offsets, or AOB signatures were extracted or are being claimed here.
- Built for game version **1.03** — the currently-installed build's version should be checked before
  assuming direct compatibility, though AOB-based tables are typically far more version-resilient
  than static-offset ones.
- Per this project's own "write our own code" policy, this table itself should never be copied,
  redistributed, or used as-is inside the mod — it's a signpost that a target is reachable, and a
  credited public source, not something to extract code or exact offsets from into this project.

## Concrete next step

When live memory investigation starts, treat "camera/FOV/change-camera-function is reachable via
plain AOB scanning" as a validated starting hypothesis, and consider Cheat Engine itself (alongside
x64dbg) as a fast first-pass tool for locating the same category of values independently, before
committing to the exact hooking architecture for the actual mod.

## Sources

- https://fearlessrevolution.com/viewtopic.php?t=15023
