# Engine Dossier — Mad Max (Avalanche Engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete (exe confirmed 64-bit, D3D11-only, no Denuvo evidence found — contradicts older community reports, see §4), external research folded in (a strong, four-independent-source feasibility case: vorpX, ReShade, Special K, and a mature Cheat Engine table all already work against this exact build) · **VR-readiness verdict:** genuinely promising — this is the best-evidenced feasibility case of any project in this portfolio so far, before a single line of our own code has run

## 1. Identity
- Game / build / version: Mad Max (2015, Avalanche Studios; published by WB Games Interactive). Steam build.
- Platform & store; unofficial port? (extra fragility/legal notes): PC via Steam, official release, no unofficial port involved.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Avalanche Engine, confirmed by a literal `"Avalanche Engine"` string in the exe**, plus internal asset/system tags like `Ai.AvalancheFuryRoad` / `Animation.AvalancheFuryRoad` / `Physics_2012.AvalancheFuryRoad` (internal codename referencing the film) and a leaked dev path `D:\dev\depot\...\Avalanche\2013_2\Source\...`. **Developer interviews (external-research, 2026-08-25) confirm Mad Max's engine build meaningfully diverges from Just Cause 3's later engine** — classic deferred shading with 3 G-buffers, no PBR, vs. JC3's clustered-deferred/4-G-buffer/PBR-capable architecture. This is why the generic Just Cause-focused Apex Engine community tooling doesn't cover Mad Max (confirmed separately, see below) — not an oversight, a real architectural difference.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **Havok physics confirmed** (`Havok StackTracer`, `HavokWorkerThread`, `Havok version: %s` strings, plus a leaked `hkgpTriangulator.inl` path — Havok Geometry Processing). **Bink (`bink2w64.dll`)** for video. **FMOD (`fmod_event64.dll`, `fmodex64.dll`)** for audio. Compiled with **VS2010** (`MSVCP100.dll`/`MSVCR100.dll`).
- Distinctive file formats / build tags / symbol naming: not yet investigated (asset archive formats). **Noted (external-research): a Mad Max-specific asset toolkit exists — Gibbed.MadMax + Mad Manager — but the generic Just Cause/Apex-Engine community tooling ecosystem (apex-tools-launcher, deca, jc-model-renderer, etc.) explicitly does NOT cover Mad Max; don't assume it transfers.** Not urgent for the camera/VR work either way.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **64-bit (PE32+, `coff-x86-64`)** — unlike Burnout Paradise (32-bit); any proxy DLL must be built for the x86_64 target. 73.3 MB on disk. Relocations stripped per file characteristics. Linker timestamp Oct 22 2015 (close to original release — see §4 for why this is a relevant data point). Unusual non-standard section names (`.data1`, `.trace`, `.xcode`, `.xpdata`, `.xtext`, `.sbss`) — `.xpdata` alone is ~69.9 MB (the bulk of the file), marked as `DATA` not executable `TEXT`; most likely embedded game data bundled directly in the exe rather than obfuscation (see §4 for why this project currently reads these names as *not* Denuvo-related, unlike the superficially similar-looking `.trace` blob found in Burnout Paradise).
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 11 confirmed, and confirmed to be the ONLY shipped renderer.** Static imports include both `d3d11.dll` and `d3d9.dll` alongside `dxgi.dll`; the literal string `D3D11CreateDevice` is present, `CreateDXGIFactory1` specifically (not the plain `CreateDXGIFactory`) is the DXGI entry point actually called. **Developer interviews (external-research, 2026-08-25) confirm D3D11 shipped as the sole PC renderer** — a D3D12 pipeline existed only as unshipped, experimental R&D at the time, so §5 onward should assume D3D11 only, not entertain a DX12 path. The `d3d9.dll` static import's purpose is unconfirmed (vestigial/utility-only is the working assumption; not yet verified live).
- Developer console / cvar system present? how opened?: **Yes — a real developer console system exists.** Exe strings show an `IConsoleCommand` class (`.?AVIConsoleCommand@Base@@`) and literal help text: *"Search the Console documentation... for the console commands: 'invoke', 'set', 'get', 'variable_list', 'function_list'"*. How it's opened in-game is not yet confirmed (untested live) — candidate for the first live session alongside the native Capture Mode (see §6/§9).

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **Genuinely unresolved — direct static evidence conflicts with external community reports, recorded honestly rather than picking a side.** External-research (2026-08-25) reports the Steam release is Denuvo-protected (Origin and GOG releases are not), citing community discussion "as recently as within the last couple of years" showing no removal patch found. **This project's own static analysis of the actually-installed exe found no corroborating evidence**: zero occurrences of the string `"Denuvo"` anywhere in the binary (Burnout Paradise's Denuvo, by contrast, was unambiguous — two literal `GetDenuvoTicketLocation`/`GetDenuvoTimeTicketRequest` exports), and the specific activation-token file external-research pointed to (`Steam\userdata\<id>\234140\dbdata`) **does not exist** on this install — that folder contains only ordinary Steam cloud-save files (`GameSave01.sav`, `GameSave02.sav`, `Settings.sav`, `remotecache.vdf`), no `dbdata` file at all. **Working hypothesis: this specific installed build (Steam auto-updates to current) may no longer have Denuvo**, possibly removed in a later patch after the community reports were written — matching the exact "shipped with Denuvo, stripped later" pattern this portfolio already documented industry-wide for Burnout Paradise. Not certain either way; treat as an open question to resolve with certainty the first time a debugger is actually attached, not a settled fact in either direction.
- Attach workflow that works: not yet tested.
- Injection vector that works (proxy DLL name / injector / framework): **Strong, specific, multi-source precedent (external-research, 2026-08-25) — the best feasibility case of any project in this portfolio so far.** Four independent tools/techniques are all confirmed working against this exact Steam build: (1) **vorpX** has a working Geometry-3D (highest-fidelity true per-eye stereo) profile with reported working head tracking in third-person — direct evidence the camera/projection system is tractable, not just that injection succeeds; (2) **ReShade** works via the standard `dxgi.dll`-proxy method (rename `ReShade64.dll` → `dxgi.dll`, drop in the game folder) — this portfolio's own usual DXGI-proxy-first pattern, independently validated here; (3) **Special K** (a more advanced overlay/injection framework) also lists Mad Max as supported; (4) a mature, actively-maintained **Cheat Engine AOB table** (FearLess Cheat Engine forums, "Mad Max 1.03") exposes Photo Mode camera range, FOV, aspect ratio, HUD removal, and — notably — a **directly-callable "change camera" game function**, via plain array-of-bytes signature scanning (no unusual obfuscation defeating that class of tool). **Concrete plan: `dxgi.dll` is the confirmed correct proxy name** (matches `CreateDXGIFactory1`, the exact entry point found statically above) — build our own from-scratch DXGI proxy next, same architecture as the Burnout Paradise M0 scaffold, targeting x86_64.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):
- **Unusually strong leads before any of our own live work has started (external-research, 2026-08-25):**
  1. **Native "Capture Mode" → "Video Mode" (`R` on keyboard)** ships an in-game, dev-exposed FOV slider that can reportedly be carried into live first-person driving gameplay (adjust in Video Mode, switch to "show HUD," resume play) — a zero-risk, zero-injection way to black-box-explore the FOV/camera range before any hooking starts. Known limits: resets on camera change, doesn't apply during binoculars/sniper, and (screenshot-only path) hides the HUD.
  2. **A mature Cheat Engine AOB table ("Mad Max 1.03")** already exposes a directly-callable **"change camera" function** plus FOV/aspect-ratio/camera-range control — the strongest single prior-art result found for this section across this whole portfolio so far. Table itself is never to be copied/used as-is (per policy) — it's a signpost that these values are reachable via ordinary AOB scanning, not something exotic.
  3. **Community Nexus/Workshop mods** ("FOV And Camera Tweaks," "Field of View (FOV) Changer") independently corroborate the same "binoculars/sniper/cinematics don't respect the FOV override" pattern across three unrelated sources (Capture Mode, both mods) — read as a real, consistent signal about how the camera system is structured (separate context-specific camera modes, not one shared code path), not coincidence. One mod's abandoned, buggy first-person-conversion attempt is itself informative: expect friction specifically around cinematics/animation-driven camera state.
  4. **vorpX's working Geometry-3D profile** (§4) is independent confirmation the underlying per-eye projection math is solvable here by a third party, even though vorpX's own implementation isn't public/reusable.

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats): not yet inspected live. **Developer-confirmed background (external-research, 2026-08-25): classic deferred shading with 3 G-buffers, explicitly without PBR** (differs from Just Cause 3's later 4-G-buffer/PBR pipeline). Deferred lighting supports "hundreds of active light sources," with hardware-scaled dynamic-shadow prioritization. Secondary/bounce lighting is approximated via a custom ground-color filter/back-projection technique (a "sun-halo" effect), not true GI.
- Shadow passes (depth-only sizes): not yet inspected live.
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes): not yet inspected live.
- UI / HUD (how it's kept separate): not yet inspected live. **Note: transparency was deliberately de-prioritized in this engine's deferred pipeline per the same developer interviews** ("very little need for transparency anyway beyond particle effects") — particle effects are the documented exception to the deferred path.

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| `invoke` | (console command, exact syntax unconfirmed) | found via exe strings; how the console itself is opened is still unconfirmed |
| `set` / `get` | read/write a named value | same source |
| `variable_list` / `function_list` | presumably enumerates available console variables/functions | same source — worth running first live, to self-document the whole cvar surface without guessing |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- **Not (yet) a dead end, but a confirmed non-transferable assumption (external-research, 2026-08-25): the generic Just Cause/Apex-Engine community modding-tool ecosystem does not cover Mad Max.** apex-tools-launcher, deca, jc-model-renderer, and the Apex Resource Index all explicitly lack Mad Max support — confirmed by developer interviews to reflect a real engine divergence (§2), not just a documentation gap. Don't waste time trying these against Mad Max archives without first confirming, quickly and empirically, that they even open a file.

## 12. Open risks toward the North Star
- **Denuvo status is genuinely unresolved, not confirmed absent** (see §4) — this project's own static evidence (no "Denuvo" string, no `dbdata` activation-token file) conflicts with external community reports of it being present on Steam. Resolve with certainty the first time a debugger is attached, rather than assuming either way going in.
- Driving games carry an elevated motion-sickness risk vs. walking-sim/shooter conversions — comfort options (FOV vignette, fixed cockpit reference frame, etc.) are likely to matter more here than in other projects, same as the Burnout Paradise front.
- Racing/open-world HUD complexity (speedometer, minimap, mission markers) may need special handling to stay legible and comfortable in a headset — worth cross-referencing against the community FOV mods' "HUD removal" toggles as a starting point.
