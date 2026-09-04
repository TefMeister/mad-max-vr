# Modding verdict for `/gr`: two topics can be flipped

Author: modding lane (`/lm`, home PC), 2026-09-04. Create-only inbox drop; fold into `INDEX.md`
and delete.

## 1. `topics/2026-08-25-native-capture-mode-camera-tool.md` → ✅ incorporated

Tried it live 2026-09-04. **Capture Mode is a real free camera** (pause menu → Log → CAPTURE
MODE): arrows/WASD move, mouse rotates, U/I tilt, Enter captures, R video mode, Esc exits.
`[verified-live 2026-09-04, n=1]`. More useful than the topic predicted: **its camera writes the
same shared constant-buffer slot 9 and the same main-pass clip matrix that gameplay writes**
(holding W for 1.5 s moved the eye 6.34 units along the matrix's forward column), so it is a
still, controllable testbed for per-eye rewrites of that constant. The FOV slider on its CAMERA
SETTINGS tab was not reached (the tab-switch key was not found: arrows move the camera, E and
Tab do nothing) — that half of the topic stays 👀 reviewed.

Write-up: `modding-notes/2026-09-04-main-pass-matrix-verified-live-and-capture-mode-is-a-free-camera.md`.

## 2. `topics/2026-09-03-the-detector-this-project-needs-is-already-built-in-enslaved.md` — the `[FLAT]` half is done

The one launch that topic said would answer §6 has run. Result: the shared per-pass clip
transform is verified live at vertex-side `GlobalConstants` slots 0..3 (six byte-identical
uploads per frame, each with slot 4 == slot 9), decomposing to hfov 80.5° / vfov 50.9° with the
eye recovered from row 3. The topic's own three lessons all paid off — pre-committed readings
made it a single launch, fingerprinting all slots caught the per-pass structure, and the raw
buffer-order dump is what made the decomposition possible. Status stays ✅ incorporated; this
just closes its open half.
