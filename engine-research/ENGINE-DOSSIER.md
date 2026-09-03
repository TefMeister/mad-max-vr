# Engine Dossier — Mad Max (Avalanche Engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 complete AND live-verified (2026-08-25) — the game launches cleanly with our proxy `dxgi.dll` in place, and the log confirms it's working exactly as intended (see §4/§5). · **VR-readiness verdict:** genuinely promising — this is the best-evidenced feasibility case of any project in this portfolio so far, and the first project where the injection foothold itself is confirmed live on the very first attempt, no EA-App-style detours needed

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
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **RESOLVED LIVE (2026-08-25) — Denuvo (or equivalent) is active.** A live debugger attach attempt against the running game was refused even fully elevated (see "Attach workflow" below for the full evidence) — this settles the question the static-only evidence below couldn't. The static analysis is kept here for the record, since it's still an interesting discrepancy worth understanding later (why didn't the usual string/file markers show up?), but it no longer represents this project's working conclusion. External-research (2026-08-25) reports the Steam release is Denuvo-protected (Origin and GOG releases are not), citing community discussion "as recently as within the last couple of years" showing no removal patch found. **This project's own static analysis of the actually-installed exe found no corroborating evidence**: zero occurrences of the string `"Denuvo"` anywhere in the binary (Burnout Paradise's Denuvo, by contrast, was unambiguous — two literal `GetDenuvoTicketLocation`/`GetDenuvoTimeTicketRequest` exports), and the specific activation-token file external-research pointed to (`Steam\userdata\<id>\234140\dbdata`) **does not exist** on this install — that folder contains only ordinary Steam cloud-save files (`GameSave01.sav`, `GameSave02.sav`, `Settings.sav`, `remotecache.vdf`), no `dbdata` file at all. **Working hypothesis: this specific installed build (Steam auto-updates to current) may no longer have Denuvo**, possibly removed in a later patch after the community reports were written — matching the exact "shipped with Denuvo, stripped later" pattern this portfolio already documented industry-wide for Burnout Paradise. Not certain either way; treat as an open question to resolve with certainty the first time a debugger is actually attached, not a settled fact in either direction.
- Attach workflow that works: **not yet found — first live attach attempt failed, and this resolves the Denuvo question (see above): something IS actively blocking debugger attachment.** 2026-08-25, live session: installed the `x64dbg-automate` plugin (dariushoule/x64dbg-automate v0.8.1, downloaded from its GitHub releases with the user's explicit go-ahead, extracted into both `x32\plugins\` and `x64\plugins\`) to get the x64dbg MCP tooling working at all — it wasn't previously installed. Plugin loads correctly (`[PLUGIN] x64dbg-automate v3 Loaded!` in the log). **`attach <pid>` against the live, running `MadMax.exe` fails with `Could not open process <pid>!` — tested twice, once non-elevated and once fully elevated (Administrator, UAC-approved), same failure both times.** Ruling out a plain elevation mismatch (the second attempt was elevated and still failed) leaves active, OS-level process-open blocking as the remaining explanation — exactly the live signal `ENGINE-DOSSIER.md`'s external-research-sourced plan said would settle the question. **Net conclusion: Denuvo (or an equivalent protection) is genuinely active on this build**, reversing this project's earlier static-analysis-only working hypothesis ("maybe it was removed in a later patch") — that hypothesis is now considered wrong. **ScyllaHide tried (2026-08-25), genuine plugin-ABI incompatibility, not a config error:** downloaded ScyllaHide v1.4 (x64dbg/ScyllaHide, last released 2023-03-24) and installed its `TitanEngine` variant into `plugins\` (renamed `.dll`→`.dp64`/`.dp32`, x64dbg only auto-loads that extension). It loads far enough for x64dbg to find it, but fails: `Export "pluginit" not found in plugin: ScyllaHideTEPluginx64`. Confirmed via `objdump`: ScyllaHide's plugin exports `TitanDebuggingCallBack`/`TitanRegisterPlugin` — an older, legacy x64dbg plugin ABI — while the currently-installed x64dbg build (and `x64dbg-automate`, which loads correctly) expects the modern `pluginit`/`plugsetup`/`plugstop` interface. **This is a real compatibility dead end with ScyllaHide's last published release, not something to keep forcing** — would need either an older x64dbg build matching ScyllaHide's expected ABI, or a rebuild of ScyllaHide against the current SDK; neither pursued (diminishing returns for this project's actual goal).
- **In-process FOV memory scan tried (2026-08-25), inconclusive — the crude "any float in a plausible range" approach isn't precise enough on its own for this game.** Extended the proxy DLL with a two-snapshot changed-value scanner (NUMPAD1/2 hotkeys, `staging/mad-max-vr/proxy-dxgi/`) that walks the process's own committed private RW memory (no `OpenProcess` needed — sidesteps the Denuvo block entirely by running from inside the process). Live test: FOV slider min→max, diffed. Result: 3,142 candidates with large (|delta|>10) changes — too many to call, and many repeat in very regular address spacing (every 0x80/0x100/0x200 bytes) with the same handful of values, a pattern that looks like an array/table of unrelated data (animation curves, physics/nav-mesh, etc.) shuffling around in the same numeric range, not a single scalar FOV variable. **Parked, not pursued further** — the user's call, since this was a side-curiosity rather than something the core VR work needs; nailing the exact address would need a proper 3-snapshot idle-noise-filtered approach (an "unchanged while idle" baseline scan before trusting a delta), real additional engineering for later if it ever becomes worth it. The scanner code itself stays in the proxy DLL (harmless, hotkey-gated) for whenever it's revisited.

**Why this doesn't actually block the mod itself (important distinction):** OS-level debugger attach (`OpenProcess`) being refused has no bearing on this project's real approach. Every technique that matters here — our own proxy DLL (already proven working live, see below), ReShade, Special K, vorpX, the Cheat Engine AOB table — works by getting code loaded **into** the game process through the normal DLL-loading mechanism (or, for Cheat Engine, its own separate non-`OpenProcess`-style method), never by an external process reaching in via `OpenProcess`. That's precisely why those all keep working under Denuvo while `x64dbg attach` doesn't. **The live debugger remains useful for read-only exploration once we're past this specific blocker (e.g. via our own already-loaded proxy DLL doing the inspection from inside the process), just not for classic external attach-and-poke.**
- Injection vector that works (proxy DLL name / injector / framework): **Strong, specific, multi-source precedent (external-research, 2026-08-25) — the best feasibility case of any project in this portfolio so far.** Four independent tools/techniques are all confirmed working against this exact Steam build: (1) **vorpX** has a working Geometry-3D (highest-fidelity true per-eye stereo) profile with reported working head tracking in third-person — direct evidence the camera/projection system is tractable, not just that injection succeeds; (2) **ReShade** works via the standard `dxgi.dll`-proxy method (rename `ReShade64.dll` → `dxgi.dll`, drop in the game folder) — this portfolio's own usual DXGI-proxy-first pattern, independently validated here; (3) **Special K** (a more advanced overlay/injection framework) also lists Mad Max as supported; (4) a mature, actively-maintained **Cheat Engine AOB table** (FearLess Cheat Engine forums, "Mad Max 1.03") exposes Photo Mode camera range, FOV, aspect ratio, HUD removal, and — notably — a **directly-callable "change camera" game function**, via plain array-of-bytes signature scanning (no unusual obfuscation defeating that class of tool). **Second injection point confirmed (external-research, 2026-08-25): a real, working 3DMigoto stereo-3D shader fix already exists for this exact D3D11 build** — [Helix Mod: Mad Max (DX11)](https://helixmod.blogspot.com/2015/10/mad-max-dx11.html) (public mirror: ThreeDeeJay/3d_fixes, `Mad Max/` folder), **86 individually-patched shaders (54 pixel, 32 vertex)**, proxying via **`d3d11.dll`** specifically (not `dxgi.dll`) — `d3d11.dll`, `d3dcompiler_46.dll`, `nvapi64.dll`, `d3dx.ini` sit alongside its `ShaderFixes/` folder. This is a second, independently-confirmed injection vector for this game, complementing our own already-proven `dxgi.dll` proxy — useful if shader-call interception specifically ever needs residency at the `d3d11.dll` boundary rather than `dxgi.dll`'s. (Studied for scope/feasibility only, per policy — never copying its shader code; no cbuffer offsets or camera-matrix specifics were published in what was accessible anyway.)

**Concrete plan: `dxgi.dll` is the confirmed correct proxy name** (matches `CreateDXGIFactory1`, the exact entry point found statically above) — build our own from-scratch DXGI proxy next, same architecture as the Burnout Paradise M0 scaffold, targeting x86_64.

**✅ LIVE-VERIFIED, first attempt, zero issues (2026-08-25):** deployed `staging/mad-max-vr/proxy-dxgi/`'s `dxgi.dll` to the game folder and launched normally (windowed, 800×600 — resolution/window mode confirmed irrelevant to this test). Game launched and ran with no visible problems. `madmax_vr_proxy_log.txt` confirms: proxy loaded (PID 29708), real system `dxgi.dll` resolved correctly, and ~25s later (past the loading screen) the game called **`CreateDXGIFactory1`** requesting `IID_IDXGIFactory1` (`{770AAE78-F26F-4DBA-A829-253C83D1B387}`, the standard public GUID) — matches the static prediction exactly. Our proxy forwarded it, got back `S_OK` and a real factory pointer, game continued normally. **This confirms the game manages its own explicit DXGI factory** (not the simpler single-call `D3D11CreateDeviceAndSwapChain` pattern Burnout Paradise uses) — the swap chain itself gets created as a separate step via that factory, and device creation happens separately via `d3d11.dll`'s `D3D11CreateDevice` (not yet observed/logged — our current proxy only watches `dxgi.dll`). **Next injection-side step, whenever resumed:** extend logging to the swap chain creation call on the returned `IDXGIFactory1` (and/or add a `d3d11.dll` proxy alongside this one) to see the actual back-buffer format/resolution/window handle the game requests — that's the natural M1 step, mirroring Burnout Paradise's approach.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

> ### Shader reflection is readable OFF DISK, despite Denuvo (2026-09-01)
>
> `[inferred-static 2026-09-01]` - from the shipped `Shaders_F.shader_bundle`; not observed live.
>
> Denuvo blocks attaching a debugger to the *executable*. It does not touch the shader bundle, which
> sits loose in the game root and carries **1363 DXBC shaders with their `RDEF` reflection chunk
> intact** (1363 RDEF / ISGN / SHEX, 0 SHDR - SM5 throughout), across **84 distinct constant-buffer
> layouts**.
>
> **The per-object camera transform is named and located:**
>
> ```
> cbuffer InstanceConsts            size 368 bytes   (112 shaders)
>     +0    WorldViewProjMatrix      64 bytes   <- 4x4
>     +288  SkyMaskProjMatrix        64 bytes   <- 4x4
> ```
>
> Other variants carry `SpotProjectionMatrix1..3`, `SpotShadowMatrix1`,
> `PointlightProjectionMatrix1` (shadow/light passes - things NOT to touch); a few small `$Globals`
> buffers hold a plain `ViewProj`/`WorldViewProj` at +0 (post/effect shaders).
>
> **⚠️ Negative result that bounds the technique:** the shared per-frame buffer `GlobalConstants`
> has **no member names to recover**. Its RDEF type record shows `Globals` is a raw `float4` array
> the engine fills from C++, not a struct. Same for `InstanceConsts` inside `cbInstanceConsts`. So
> reflection names the per-object matrix but **cannot** name a shared view matrix; if one exists it
> must be found by value.
>
> **✏️ Corrected 2026-09-03 (`/pd`, dev PC): `GlobalConstants` is TWO layouts, not one.** The earlier
> "651 shaders, 2352 bytes, `float4 Globals[20]`" conflated them; 465 + 186 = 651, so this is the
> same population read more carefully. `[inferred-static 2026-09-03]`
>
> ```
> cbuffer GlobalConstants   size 2352 bytes  (465 shaders)
>     +0     Globals            272 bytes   <- 17 float4 slots
>     +272   LightPositions    1040 bytes
>     +1312  LightColors       1040 bytes
>
> cbuffer GlobalConstants   size  512 bytes  (186 shaders)
>     +0     Globals            320 bytes   <- 20 float4 slots
>     +320   ShadowTransform    192 bytes
> ```
>
> So the by-value search is **17 slots in one buffer and 20 in another**, not ~20 in one.
> `ShadowTransform` (192 bytes = three 4x4s) makes the 512-byte layout very likely the
> shadow-pass variant — worth knowing before reading any result off it.
>
> **📍 Register bindings, added 2026-09-03 (new `dxbc-reflect.py bind` mode).**
> `[inferred-static 2026-09-03]` `GlobalConstants` binds to **`b0` in all 651 shaders** — unanimous,
> no exceptions. `cbInstanceConsts` is `b1` in 823 shaders (`b3` in 63, `b2` in 7) and the unwrapped
> `InstanceConsts` is `b1` in all 176. ⚠️ `b0` is not exclusively `GlobalConstants` — a buffer called
> `cb0` also binds `b0` in 16 shaders — so a future patch must key on more than the register.
> Corroboration: the mode checks every binding name against a cbuffer in the same shader and all
> 1363 shaders matched, which is what says the record layout is being read correctly rather than
> plausibly. Re-running `summary` and `find GlobalConstants` after the tool edit reproduced the
> pre-edit output byte-for-byte. Dump: `dev-archive/recon/2026-09-03-cbfp-fingerprint-pass/`.
> **✅ The by-value probe is now written, and it is static work** (`/pd`, 2026-09-03): the existing
> `dxgi.dll` proxy gained a constant-buffer fingerprint pass that, per frame, reports which 16-byte
> slots were byte-identical across every write, and on a user mark which of those changed between two
> marked frames. Constant-within-frame AND changed-between-marks is the shared-camera signature.
> Builds clean `[compile-verified 2026-09-03]`; its logic is tested offline against constructed
> ground truth by a harness that includes the shipped source `[verified-numerically 2026-09-03,
> n=17]`; **it has never been run against the game.** Source `staging/mad-max-vr/proxy-dxgi/src/cbfp.c`,
> write-up `modding-notes/2026-09-03-constant-buffer-fingerprint-pass.md`. What remains is one launch.
>
> Tool: `flat-to-vr-RE-toolkit/tools/dxbc-reflect.py` (`summary` / `find` / `list`).
> Write-up: `modding-notes/2026-09-01-shader-reflection-off-disk-despite-denuvo.md`.

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
  5. **The single best lead so far (external-research, 2026-08-25): a real, working 3DMigoto stereo-3D shader fix already exists for this exact D3D11 build** ([Helix Mod: Mad Max (DX11)](https://helixmod.blogspot.com/2015/10/mad-max-dx11.html), mirrored at ThreeDeeJay/3d_fixes) — 86 individually-identified-and-patched shaders (54 pixel, 32 vertex), each named by shader hash. Unlike Burnout Paradise (where no D3D11-era stereo fix exists at all), someone has already gone shader-by-shader through this exact binary and made per-eye-relevant changes stick. It doesn't hand over the actual camera/projection cbuffer answer (3D Vision's projection-shift trick isn't the same problem as true per-eye VR rendering, and no offsets were published anywhere this project could access) — but it substantially de-risks the *scope* of §6/§7's live shader-reflection work: the shader surface is finite, individually addressable, and proven not to resist this class of analysis. See §8 for the per-pass breakdown this fix's writeup also revealed, and §11 for a DOF-related gotcha worth remembering early.

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap): **unknown, but instrumented as of 2026-09-03.** The §6 fingerprint pass hooks
  both `Map`/`Unmap` and `UpdateSubresource` and logs which path each tracked buffer is filled
  through, plus the number of writes per frame - so the same single launch that answers §6 also
  answers this, without a separate investigation. ⚠️ A partial `UpdateSubresource` (non-NULL
  `pDstBox`) is counted but deliberately not recorded as a whole-buffer write; if the log shows those,
  the pass needs an offset model before its slot values mean anything.
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats): not yet inspected live. **Developer-confirmed background (external-research, 2026-08-25): classic deferred shading with 3 G-buffers, explicitly without PBR** (differs from Just Cause 3's later 4-G-buffer/PBR pipeline). Deferred lighting supports "hundreds of active light sources," with hardware-scaled dynamic-shadow prioritization. Secondary/bounce lighting is approximated via a custom ground-color filter/back-projection technique (a "sun-halo" effect), not true GI.
- Shadow passes (depth-only sizes): not yet inspected live.
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes): not yet inspected live.
- UI / HUD (how it's kept separate): not yet inspected live. **Note: transparency was deliberately de-prioritized in this engine's deferred pipeline per the same developer interviews** ("very little need for transparency anyway beyond particle effects") — particle effects are the documented exception to the deferred path.
- **Real per-pass breakdown, third-party-confirmed (external-research, 2026-08-25, from the Helix/3DMigoto fix's own writeup — see §4/§6):** distinct passes/issues had to be handled individually to get stereo right, itemized as: shadows/lighting, lens-flare separation, fire-effect "halo" reduction (bright fire causing eye strain in stereo), decal depth, and skybox/sun stereo separation. HUD/UI is its own separate depth-plane problem, handled via 3DMigoto's `IniParams` mechanism (runtime-adjustable shader constants) with dedicated hotkeys for target-icon/crosshair depth and a full HUD toggle. The render-pass *taxonomy* here transfers directly to this project's own work even though the underlying technique (3D-Vision projection-shift) differs from true per-eye VR rendering.

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| `invoke` | (console command, exact syntax unconfirmed) | found via exe strings; how the console itself is opened is still unconfirmed |
| `set` / `get` | read/write a named value | same source |
| `variable_list` / `function_list` | presumably enumerates available console variables/functions | same source — worth running first live, to self-document the whole cvar surface without guessing |

**How the console is actually reached (external-research, 2026-08-25):** the in-game keybind to open this console is still unconfirmed, but a community tool, **MMConsole** (Nexus Mods, "command console" mod), already reaches it a different way — thread-injection into the running process, exposing `invoke`/`set`/`get`/`variable_list`/`function_list` through its own separate console window, confirmed supported against the Steam build specifically (its "dumper" feature is GOG/Origin-only, which is itself a small independent Denuvo-shaped data point, consistent with §4's live-confirmed conclusion). Not adopted or copied — this project's own from-scratch tooling remains the plan — but it's confirmed proof this console surface is genuinely live-reachable, not just a static artifact.

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- **Early gotcha to remember, not yet understood (external-research, 2026-08-25, from the Helix/3DMigoto fix's writeup):** that fix requires the game's own **Depth of Field setting to be left at "normal"** — other DOF settings reportedly cause landscape depth *inversion* in stereo. The underlying cause isn't understood yet, and it's specific to 3D-Vision's technique, not confirmed to carry over to a true-VR approach — but worth testing for early rather than discovering mid-project if this engine's DOF pass turns out to interact with depth/stereo in a similarly fragile way for us.
- **Not (yet) a dead end, but a confirmed non-transferable assumption (external-research, 2026-08-25): the generic Just Cause/Apex-Engine community modding-tool ecosystem does not cover Mad Max.** apex-tools-launcher, deca, jc-model-renderer, and the Apex Resource Index all explicitly lack Mad Max support — confirmed by developer interviews to reflect a real engine divergence (§2), not just a documentation gap. Don't waste time trying these against Mad Max archives without first confirming, quickly and empirically, that they even open a file.

## 12. Open risks toward the North Star
- **Denuvo status is genuinely unresolved, not confirmed absent** (see §4) — this project's own static evidence (no "Denuvo" string, no `dbdata` activation-token file) conflicts with external community reports of it being present on Steam. Resolve with certainty the first time a debugger is attached, rather than assuming either way going in.
- Driving games carry an elevated motion-sickness risk vs. walking-sim/shooter conversions — comfort options (FOV vignette, fixed cockpit reference frame, etc.) are likely to matter more here than in other projects, same as the Burnout Paradise front.
- Racing/open-world HUD complexity (speedometer, minimap, mission markers) may need special handling to stay legible and comfortable in a headset — worth cross-referencing against the community FOV mods' "HUD removal" toggles as a starting point.
