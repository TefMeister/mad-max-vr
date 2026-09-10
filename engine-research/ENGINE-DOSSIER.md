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

  **✅ SETTLED RATHER THAN PENDING, and there is an ABI conflict beside it (drained from `/gr`
  inbox, 2026-09-07).** ScyllaHide is **dormant upstream**: latest release still **v1.4,
  2023-03-24**, last `master` commit **2023-07-29**, not archived, 53 open issues
  `[verified-live 2026-09-07, n=1 GitHub API read]`. Waiting for a ScyllaHide release is therefore
  not a realistic unblock, and of the two routes named above, *"rebuild against the current SDK"*
  has no upstream momentum — it would be our work, not someone else's.

  ⚠️ **The two plugins want opposite ABIs, so you can have anti-anti-debug OR scripted debugging
  on a given install, not both.** ScyllaHide exports the **legacy** `TitanRegisterPlugin` interface
  and needs an **older** x64dbg; `x64dbg-automate` targets the **modern** `pluginit` interface and
  loads correctly against the current build. **So the one remaining viable route — downgrading
  x64dbg to match ScyllaHide — would break the automation bridge every project drives the debugger
  with.** `[inferred-static 2026-09-07]`, a consequence of the two recorded export sets rather than
  an observation.

  **If ScyllaHide is ever genuinely needed, the route is a second, pinned-old install kept apart
  from the automation one — never a downgrade of the working install.** The machine is already
  half-way there by accident: two x64dbg installs exist, and only the WinGet copy carries
  ScyllaHide `[measured 2026-09-07]`. ⚠️ Both bitnesses of that copy hold a **zero-byte
  `scylla_hide.log`**, which is consistent with the plugin **failing at load**, not with it having
  worked — nothing reaches the log if `pluginit` is never found.

  ⚠️ **This matters most to `burnout-paradise-vr`**, whose dossier still plans to load ScyllaHide
  *"before assuming Denuvo blocks attach outright"*. That plan is not merely blocked — unblocking
  it would cost every project its debugger tooling.
- **In-process FOV memory scan tried (2026-08-25), inconclusive — the crude "any float in a plausible range" approach isn't precise enough on its own for this game.** Extended the proxy DLL with a two-snapshot changed-value scanner (NUMPAD1/2 hotkeys, `staging/mad-max-vr/proxy-dxgi/`) that walks the process's own committed private RW memory (no `OpenProcess` needed — sidesteps the Denuvo block entirely by running from inside the process). Live test: FOV slider min→max, diffed. Result: 3,142 candidates with large (|delta|>10) changes — too many to call, and many repeat in very regular address spacing (every 0x80/0x100/0x200 bytes) with the same handful of values, a pattern that looks like an array/table of unrelated data (animation curves, physics/nav-mesh, etc.) shuffling around in the same numeric range, not a single scalar FOV variable. **Parked, not pursued further** — the user's call, since this was a side-curiosity rather than something the core VR work needs; nailing the exact address would need a proper 3-snapshot idle-noise-filtered approach (an "unchanged while idle" baseline scan before trusting a delta), real additional engineering for later if it ever becomes worth it. The scanner code itself stays in the proxy DLL (harmless, hotkey-gated) for whenever it's revisited.

**Why this doesn't actually block the mod itself (important distinction):** OS-level debugger attach (`OpenProcess`) being refused has no bearing on this project's real approach. Every technique that matters here — our own proxy DLL (already proven working live, see below), ReShade, Special K, vorpX, the Cheat Engine AOB table — works by getting code loaded **into** the game process through the normal DLL-loading mechanism (or, for Cheat Engine, its own separate non-`OpenProcess`-style method), never by an external process reaching in via `OpenProcess`. That's precisely why those all keep working under Denuvo while `x64dbg attach` doesn't. **The live debugger remains useful for read-only exploration once we're past this specific blocker (e.g. via our own already-loaded proxy DLL doing the inspection from inside the process), just not for classic external attach-and-poke.**
- Injection vector that works (proxy DLL name / injector / framework): **Strong, specific, multi-source precedent (external-research, 2026-08-25) — the best feasibility case of any project in this portfolio so far.** Four independent tools/techniques are all confirmed working against this exact Steam build: (1) **vorpX** has a working Geometry-3D (highest-fidelity true per-eye stereo) profile with reported working head tracking in third-person — direct evidence the camera/projection system is tractable, not just that injection succeeds; (2) **ReShade** works via the standard `dxgi.dll`-proxy method (rename `ReShade64.dll` → `dxgi.dll`, drop in the game folder) — this portfolio's own usual DXGI-proxy-first pattern, independently validated here; (3) **Special K** (a more advanced overlay/injection framework) also lists Mad Max as supported; (4) a mature, actively-maintained **Cheat Engine AOB table** (FearLess Cheat Engine forums, "Mad Max 1.03") exposes Photo Mode camera range, FOV, aspect ratio, HUD removal, and — notably — a **directly-callable "change camera" game function**, via plain array-of-bytes signature scanning (no unusual obfuscation defeating that class of tool). **Second injection point confirmed (external-research, 2026-08-25): a real, working 3DMigoto stereo-3D shader fix already exists for this exact D3D11 build** — [Helix Mod: Mad Max (DX11)](https://helixmod.blogspot.com/2015/10/mad-max-dx11.html) (public mirror: ThreeDeeJay/3d_fixes, `Mad Max/` folder), **86 individually-patched shaders (54 pixel, 32 vertex)**, proxying via **`d3d11.dll`** specifically (not `dxgi.dll`) — `d3d11.dll`, `d3dcompiler_46.dll`, `nvapi64.dll`, `d3dx.ini` sit alongside its `ShaderFixes/` folder. This is a second, independently-confirmed injection vector for this game, complementing our own already-proven `dxgi.dll` proxy — useful if shader-call interception specifically ever needs residency at the `d3d11.dll` boundary rather than `dxgi.dll`'s. (Studied for scope/feasibility only, per policy — never copying its shader code; no cbuffer offsets or camera-matrix specifics were published in what was accessible anyway.)

**Concrete plan: `dxgi.dll` is the confirmed correct proxy name** (matches `CreateDXGIFactory1`, the exact entry point found statically above) — build our own from-scratch DXGI proxy next, same architecture as the Burnout Paradise M0 scaffold, targeting x86_64.

**✅ LIVE-VERIFIED, first attempt, zero issues (2026-08-25):** deployed `staging/mad-max-vr/proxy-dxgi/`'s `dxgi.dll` to the game folder and launched normally (windowed, 800×600 — resolution/window mode confirmed irrelevant to this test). Game launched and ran with no visible problems. `madmax_vr_proxy_log.txt` confirms: proxy loaded (PID 29708), real system `dxgi.dll` resolved correctly, and ~25s later (past the loading screen) the game called **`CreateDXGIFactory1`** requesting `IID_IDXGIFactory1` (`{770AAE78-F26F-4DBA-A829-253C83D1B387}`, the standard public GUID) — matches the static prediction exactly. Our proxy forwarded it, got back `S_OK` and a real factory pointer, game continued normally. **This confirms the game manages its own explicit DXGI factory** (not the simpler single-call `D3D11CreateDeviceAndSwapChain` pattern Burnout Paradise uses) — the swap chain itself gets created as a separate step via that factory, and device creation happens separately via `d3d11.dll`'s `D3D11CreateDevice` (not yet observed/logged — our current proxy only watches `dxgi.dll`). **Next injection-side step, whenever resumed:** extend logging to the swap chain creation call on the returned `IDXGIFactory1` (and/or add a `d3d11.dll` proxy alongside this one) to see the actual back-buffer format/resolution/window handle the game requests — that's the natural M1 step, mirroring Burnout Paradise's approach.

### ⚠️ 4a. LATENT: our proxy never frees the real `dxgi.dll` — a reload would walk straight past us (drained from `/sr` inbox, 2026-09-04)

`proxy-dxgi/src/proxy.c` loads the real module from the system directory by full path
(`LoadLibraryA(sysdir)`, ~line 84) and **contains no `FreeLibrary` anywhere**
`[inferred-static 2026-09-04, read directly]`. An estate-wide audit read all ten proxies: of the
eight that load the real system module by path, **exactly one releases it.**

**Why that can silently remove the mod.** `LoadLibrary` remarks: *"When no path is specified, the
function searches for loaded modules whose base name matches … If the name matches, the load
succeeds."* So if the game ever `FreeLibrary`s **our** proxy — a startup capability probe, a
renderer restart, an options change — the system copy stays resident under the base name
`dxgi.dll`, the game's next `LoadLibrary("dxgi.dll")` matches **it**, the application directory is
never searched, **our proxy never loads again, and the game runs perfectly without us.**

**The diagnostic signature is the part worth remembering:** per launch the proxy log holds a load,
one or two export calls, and an unload inside ~100 ms — then nothing, while the game visibly
reaches gameplay. That reads as "the game crashed my mod" or "this game must use a different
graphics API". It means neither: **you were reloaded past.**

Prior art: ReShade carried this exact defect until commit `74347b91d` (2019-12-19, shipped 4.5.2),
titled *"Fix hooking in Alan Wake"*.

**Fix: `FreeLibrary` the real module in `DLL_PROCESS_DETACH`. One line.** (The structural
alternative is to load a *renamed* original rather than the system one, which is why
`XIII2003-vr`'s proxy is immune — no resident module ever shares its base name.)

⚠️ **Latent, not live** — it only bites on a game that probes-and-reloads, and so far that is
Alan Wake. But **this proxy is the one carrying our live camera work**, so a silent bypass would be
read as a probe regression, and the symptom points away from the cause. Worth closing anyway.

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
> **`[disproved 2026-09-03c]` — the 512-byte layout is the VERTEX-shader view, not a shadow
> variant; see the correction block below.**
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
> **✏️ Corrected 2026-09-03c (`/pd`, home PC, static — the shaders DISASSEMBLED, not just reflected).**
> `[inferred-static 2026-09-03, n=651 shaders]` via the new `dxbc-usage.py`; evidence in
> `dev-archive/recon/2026-09-03c-stage-split-and-slot-usage/`; write-up
> `modding-notes/2026-09-03c-the-two-layouts-are-vertex-and-pixel-and-the-camera-matrix-is-per-pass.md`.
>
> - **The two layouts are the two STAGES.** All 186 shaders declaring 512 bytes are vertex
>   shaders; all 465 declaring 2352 bytes are pixel shaders. `ShadowTransform` (slots 20..31 of
>   the vertex side) is the three cascade matrices that 57 vertex shaders project into.
> - **No shipped shader declares a 3136-byte cbuffer** (84 layouts, 1363 shaders). The 3136-byte
>   buffer the first live run saw created 1:1 with the 512-byte one is read as the **pixel-side
>   allocation, larger than the 2352 bytes the shaders declare** (legal in D3D11) —
>   `[hypothesis]` until the bind census confirms `PS b0 <- 3136`. `3136 = 320 + 2×1408` fits a
>   20-slot `Globals` plus 88-entry light arrays; arithmetic, not evidence.
> - **Slots 16..19 are NOT a matrix.** `[disproved 2026-09-03c]` Slots 18 and 19 are read by no
>   shader at all; 16 and 17 are `xyz offset + w scale` for a projected coordinate in 13 vertex
>   shaders. The 4×4 shape was layout coincidence.
> - **The clip-space transform is at vertex-side slots 0..3, per PASS.** Fifteen vertex shaders
>   run `pos.x·cb0[0] + pos.y·cb0[1] + pos.z·cb0[2] + cb0[3]` (row-vector storage, translation in
>   the fourth slot); in shaders 0009 and 0023 the product is written straight to `SV_Position`.
>   The first live run's log shows slots 0..5 varying WITHIN gameplay frames (written ~10× per
>   frame) — a per-pass camera, which the probe's constant-within-frame filter excluded by
>   design. Slot 4 is a per-pass position subtracted from world positions (view origin); slot 9
>   is the frame-constant main camera position (146 vertex shaders subtract it), matching the
>   live reading. Slots 12/13 are packed fog/fade parameters.
> - **Most vertex shaders do NOT use that shared matrix for their position.** On the register
>   chain feeding `SV_Position`: `InstanceConsts` b1 slots 0..3 (the per-object
>   `WorldViewProjMatrix`) in 109 shaders and `cbInstanceConsts` b1 slots 0..3 in ~35, versus
>   `GlobalConstants` slots 0..3 in 15. **A VR patch has two delivery paths to cover**, and the
>   per-object one needs its WVP re-derived per draw — whether a separable world matrix exists in
>   `InstanceConsts` slots 4..15 is the queued static question.
> - **The probe was extended** (`staging 4533ec9`, `[compile-verified]`, self-test 30/30, not
>   run): 3136 tracked, a (stage, slot, size) bind census on `VS/PSSetConstantBuffers`, and a
>   per-write dump on `NUMPAD3` that flags the write whose slot-4 view origin equals the slot-9
>   camera — the main-pass clip transform candidate. One dump answers both open points.
>
> Tool: `flat-to-vr-RE-toolkit/tools/dxbc-reflect.py` (`summary` / `find` / `list`) and
> `dxbc-usage.py` (stage split, per-slot reads, instruction samples, `SV_Position` chain).
> Write-up: `modding-notes/2026-09-01-shader-reflection-off-disk-despite-denuvo.md`.

> ### LIVE VERIFICATION, 2026-09-04 (home PC, `/lm`) — the main-pass matrix is where the disassembly said, and Capture Mode drives it
>
> One launch of the 2026-09-03c probe (`staging 4533ec9`), four dumps, one A/B. Write-up:
> `modding-notes/2026-09-04-main-pass-matrix-verified-live-and-capture-mode-is-a-free-camera.md`;
> evidence `dev-archive/recon/2026-09-04-main-pass-matrix-live-and-capture-mode/`.
>
> - **Stage split confirmed:** `VS b0 <- 512-byte` and `PS b0 <- 3136-byte`, first sightings 1 ms
>   apart, identical bind counts all session; `PS b0 <- 2352` never seen. `[verified-live 2026-09-04, n=1 launch]`
> - **Main-pass clip transform = vertex-side slots 0..3, uploaded 6× per gameplay frame** (writes
>   3/5/7/9/11/13 of 14, byte-identical, each with slot 4 == slot 9). Writes 0..2 are the three
>   shadow cascades (orthographic scale, sun-fixed rotation rows); writes 4/6/8/10/12 are five
>   further perspective cameras near the eye (`[hypothesis]` local-light shadows). `[verified-live 2026-09-04, n=4 dumps]`
> - **Decomposition** `[measured 2026-09-04, n=4]`: column 3 = unit forward (clip.w = distance along
>   forward, positive in front); |column 0| = 1.1809 → **hfov 80.5°**; |column 1| = 2.0994 →
>   **vfov 50.9°**, aspect 1.7778; columns orthogonal to 5 decimals; **row 3 = −camera · column**,
>   recovering the slot-9 position exactly. **Y up.** right × up = −forward in world coordinates.
>   Column 2 ≈ 0 with row 3's z a small positive constant (0.089–0.117, drifting frame to frame):
>   reversed-Z with infinite far is the shape, `[hypothesis]`; the drift is unexplained.
> - **Capture Mode (pause menu → Log → CAPTURE MODE) is a free camera** — arrows/WASD move, mouse
>   rotates, U/I tilt — **and it writes the same slot 9 and the same main-pass matrix** (W for 1.5 s
>   moved the eye 6.34 units along the forward column). Same FOV as gameplay. A ready testbed for
>   per-eye rewrites. `[verified-live 2026-09-04, n=1]` Tab-switch key not found (E, Tab, arrows tried).
> - A/B regression reproduced the dev PC list exactly (9,12,13,16,17,18,19,23,27,31). `[verified-live 2026-09-04, n=2 machines]`

> ### LIVE, 2026-09-04b (dev PC, `/lm`) — the Capture Mode FOV slider edits `P` only; V untestable in this save
>
> Same build rebuilt here (237,056 B). Write-up:
> `modding-notes/2026-09-04b-capture-mode-fov-slider-moves-the-projection-columns.md`; evidence
> `dev-archive/recon/2026-09-04b-devpc-capture-mode-fov-slider/`.
>
> - **FIELD OF VIEW slider → |col 0| 1.7936 … 0.6138 = hfov 58.28° … 116.91°**, vfov in lock-step at the
>   window aspect (1.3975 at 784×561), eye and forward unchanged, ≈3° of hfov per `>` click near the
>   default. `[measured 2026-09-04, n=6 dumps]` `Esc` out of Capture Mode restores 80.48° immediately.
> - **The tab is mouse-driven:** click the tab label; click a row label to select it; click the `<` / `>`
>   arrows at the ends of its bar to change it. Bar clicks, knob drags, keyboard Down/Right do nothing
>   there. `[verified-live 2026-09-04, n=1 session]`
> - **Clip-z constant (row 3 z) is per POSITION, not per frame:** 0.0889 at one garage position, 0.1140
>   at another, and 0.1140 across twelve dumps over ten minutes at the latter, gameplay and Capture Mode
>   alike. `[measured 2026-09-04, n=2 positions, 13 dumps]` Meaning still `[hypothesis]`.
> - **V: on foot nothing (expected); in a car NOT TESTED** — this save's garage car is a non-enterable
>   prop (user-confirmed). `settings.ini` `[KeyMapping]` decodes alphabetically (A=0…Z=25) and puts
>   `vehicle_fp_cam` on V, `enter_vehicle` on R `[inferred-static 2026-09-04]`, so the report is at least
>   config-backed. X (keymap `overview_camera`) does not open Capture Mode from the keyboard (n=1).

- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
  **BOTH** `[inferred-static 2026-09-03c]` — per-draw WVP in `InstanceConsts`/`cbInstanceConsts` b1
  slots 0..3 for the bulk of the scene (~144 vertex shaders), and a shared per-PASS clip transform
  at `GlobalConstants` b0 slots 0..3 (vertex side, 512 B) for 15 world-space shaders. Fill path:
  `Map`/`Unmap`, ~10 writes per frame `[verified-live 2026-09-03b]`.
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
  Shared: `b0` +0..+63 (slots 0..3), unnamed (`float4 Globals[20]`), consumed as
  `pos.x·M[0] + pos.y·M[1] + pos.z·M[2] + M[3]` — row-vector storage, translation in slot 3.
  Per-object: `b1` +0 `WorldViewProjMatrix` (named) / `InstanceConsts[0..3]` (unnamed), same
  consumption pattern. Live decomposition of the shared matrix (2026-09-04 block above): unit forward in
  column 3, focal scales 1.1809 / 2.0994 in columns 0/1, eye in row 3, Y up, right × up = −forward
  `[measured 2026-09-04, n=4]`. Where `P` comes from as a separate matrix: still not observed — only the product is uploaded.
- Where projection `P` / FOV comes from: only `V·P` is uploaded on the shared path; its focal scales read
  **hfov 80.5° / vfov 50.9° at 16:9** in gameplay and in Capture Mode alike `[measured 2026-09-04, n=4]`.
  **Capture Mode's CAMERA SETTINGS → FIELD OF VIEW slider changes exactly these two columns and nothing
  else** — hfov **58.28° … 116.91°** (default 80.48°), eye and forward column untouched, `r3z` untouched
  `[measured 2026-09-04, n=6 dumps, 5 slider positions]`. **hfov is the anchored value; vfov follows the
  window aspect** (62.40° at 784×561, 50.9° at 16:9, same 80.5° hfov) `[measured 2026-09-04, n=2 aspects]`.
  Leaving Capture Mode with `Esc` restores the default at once — the slider does not carry into
  gameplay by that route `[verified-live 2026-09-04, n=1]`. Notes: `modding-notes/2026-09-04b-…`.
- The per-eye override maths (`K_eye = …`):
- **A native first-person DRIVING camera reportedly exists: `V` on the keyboard toggles it while in the car** `[reported 2026-09-04]` — config-backed (`settings.ini` `vehicle_fp_cam` = V) and pressed on foot on 2026-09-04b with no effect, as expected; the in-car press is still owed and needs a save with a drivable car (user, from community knowledge; not yet pressed by a session). If real, it is the closest thing the game ships to a VR seat: check with the probe whether slot 9 and the main-pass matrix move to the driver position, and whether the FOV columns change.
- **Unusually strong leads before any of our own live work has started (external-research, 2026-08-25):**
  1. **Native "Capture Mode" → "Video Mode" (`R` on keyboard)** ships an in-game, dev-exposed FOV slider that can reportedly be carried into live first-person driving gameplay (adjust in Video Mode, switch to "show HUD," resume play) — a zero-risk, zero-injection way to black-box-explore the FOV/camera range before any hooking starts. Known limits: resets on camera change, doesn't apply during binoculars/sniper, and (screenshot-only path) hides the HUD.
  2. **A mature Cheat Engine AOB table ("Mad Max 1.03")** already exposes a directly-callable **"change camera" function** plus FOV/aspect-ratio/camera-range control — the strongest single prior-art result found for this section across this whole portfolio so far. Table itself is never to be copied/used as-is (per policy) — it's a signpost that these values are reachable via ordinary AOB scanning, not something exotic.
  3. **Community Nexus/Workshop mods** ("FOV And Camera Tweaks," "Field of View (FOV) Changer") independently corroborate the same "binoculars/sniper/cinematics don't respect the FOV override" pattern across three unrelated sources (Capture Mode, both mods) — read as a real, consistent signal about how the camera system is structured (separate context-specific camera modes, not one shared code path), not coincidence. One mod's abandoned, buggy first-person-conversion attempt is itself informative: expect friction specifically around cinematics/animation-driven camera state.
  4. **vorpX's working Geometry-3D profile** (§4) is independent confirmation the underlying per-eye projection math is solvable here by a third party, even though vorpX's own implementation isn't public/reusable.
  5. **The single best lead so far (external-research, 2026-08-25): a real, working 3DMigoto stereo-3D shader fix already exists for this exact D3D11 build** ([Helix Mod: Mad Max (DX11)](https://helixmod.blogspot.com/2015/10/mad-max-dx11.html), mirrored at ThreeDeeJay/3d_fixes) — 86 individually-identified-and-patched shaders (54 pixel, 32 vertex), each named by shader hash. Unlike Burnout Paradise (where no D3D11-era stereo fix exists at all), someone has already gone shader-by-shader through this exact binary and made per-eye-relevant changes stick. It doesn't hand over the actual camera/projection cbuffer answer (3D Vision's projection-shift trick isn't the same problem as true per-eye VR rendering, and no offsets were published anywhere this project could access) — but it substantially de-risks the *scope* of §6/§7's live shader-reflection work: the shader surface is finite, individually addressable, and proven not to resist this class of analysis. See §8 for the per-pass breakdown this fix's writeup also revealed, and §11 for a DOF-related gotcha worth remembering early.

### 6b. The per-object path has NO separable world matrix (answered 2026-09-04c, static)

`[inferred-static 2026-09-04, n=113 shaders for InstanceConsts + 188 for cbInstanceConsts]`
The board asked whether `InstanceConsts` carries a world or world-view matrix, because that would
make `WVP_eye = W · VP_eye` computable per draw. **It does not.**

| slots | what the shader code actually does with them | verdict |
| --- | --- | --- |
| **0..3** | `mul/mad/mad/add` row-vector chain straight into `SV_Position` (112 of 112 shaders) | the full **object→clip** 4×4 |
| **4..15** | **four repeated 3-slot groups**: `add(-pos, A)`, a `w`-difference blend, `add_sat(dp3(-delta, dir), bias)` (56 shaders) | position/direction falloff data, **not a transform** |
| **16, 17** | sign tests, a scalar multiply, a per-vertex colour scale (106 shaders) | material/instance scalars; 17 is on the position path in 75 |
| **18..21** | a 3×4 affine `mad/mul/mad/add` (16 shaders) — but applied to a **camera-relative** position and written to **`o3`**, a texcoord | a projector/probe space, **not the object's world matrix** |
| **22** | `lt`/`add`/`mul_sat` against `|value|` (82 shaders) | a fade threshold |

The other per-object buffer, **`cbInstanceConsts`** (188 vertex shaders across nine sizes from 16 to
160 bytes, register `b1` or `b3`), likewise puts its clip transform at **slots 0..3** in every size.

**The complete per-object position path** is therefore just:
`clip = (v0 + cbLightingConsts[3].xyz) · InstanceConsts[0..3]`, with an instance scale at slot 17 in
75 shaders. `cbLightingConsts` is a nameless 64-byte block whose slots 0..2 are colour work (a
two-colour lerp and a multiplier) and whose **slot 3 alone is a pre-translation** of the object-space
vertex position — read by 112 shaders, the whole population.

⇒ **The per-object path must be reached by hooking its CPU-side fill**, which is the branch the row
named. §7a's one-element edit then applies to it unchanged — the same element, handed the shared
frame's `w`.

⚠️ **This corrects a tool, not just a gap.** `dxbc-usage.py`'s `SV_Position` walk was over-reporting
(it ignored program order and counted writes that happen *after* the position write). Before the fix
it listed slots 4..15 and 18..21 as feeding `SV_Position`; they do not. Sections A/B/C of that tool
reproduce byte-for-byte, so **every 2026-09-03c conclusion drawn from them stands**. Fix, a 6-case
regression test and both census outputs: `dev-archive/recon/2026-09-04c-one-element-stereo/`.

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap): **unknown, but instrumented as of 2026-09-03.** The §6 fingerprint pass hooks
  both `Map`/`Unmap` and `UpdateSubresource` and logs which path each tracked buffer is filled
  through, plus the number of writes per frame - so the same single launch that answers §6 also
  answers this, without a separate investigation. ⚠️ A partial `UpdateSubresource` (non-NULL
  `pDstBox`) is counted but deliberately not recorded as a whole-buffer write; if the log shows those,
  the pass needs an offset model before its slot values mean anything.
- **Answered 2026-09-04:** `Map`/`Unmap`, 14 whole-buffer writes per gameplay frame of the 512-byte
  buffer (10–11 on the dev PC), zero `UpdateSubresource` `[verified-live 2026-09-04, n=2 machines]`.
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?: yes — the probe reads every write from the `Map` pointer at `Unmap` time `[verified-live 2026-09-04]`.
- The chosen override patch point and why: `Unmap` of the 512-byte VS buffer, for every write where
  slot 4 == slot 9 (the six main-eye uploads) — decided from the 2026-09-04 dump.
  **BUILT 2026-09-04c** (`/pd`, static): `cbfp.c`'s `hk_Unmap` applies the edit in place on the
  still-valid mapping, before `real_Unmap`, gated on the same `slot 4 == slot 9` discriminator the
  diagnostic dump has used since 2026-09-03c — so the shadow cascades and the five local
  perspective cameras are deliberately left alone. OFF until **NUMPAD6**; NUMPAD7 cycles
  wiggle/left/right, NUMPAD8/9 scale the separation. `[compile-verified 2026-09-04]`,
  63 self-test assertions `[verified-numerically 2026-09-04]`, **never run.**

### ⭐ 7a. The per-eye edit is ONE FLOAT — and that supersedes the "rebuild V_eye · P" plan

`[verified-numerically 2026-09-04, n=33 Python cases + 26 C assertions]`

Matrices here are row-vector (`clip = pos · M`, established 2026-09-03c from the
`mul/mad/mad/add` chain into `SV_Position`). A per-eye camera shift is `V_eye = V · T` with `T` a
translation of `d` along the **view** x axis, so

```
M_eye = W · V · T · P = M + W · (V·T − V) · P
```

`(V·T − V)` has exactly one non-zero entry, `[3][0] = d`. For any **affine** `W` (fourth column
`[0,0,0,1]ᵀ` — true of every object transform) the product keeps that shape, and post-multiplying
by `P` turns it into "row 3 += d × (row 0 of P)". Row 0 of a perspective projection is
`[w,0,0,0]` for symmetric **and** off-centre frusta alike, because an off-centre frustum puts its
shift in row 2. So the entire stereo edit is:

```
M[3][0] += d * w          w = |column 0| = the horizontal focal term (1.1809 live)
```

- **Why this is better than the plan it replaces.** The 2026-09-04 board row proposed rebuilding
  `V_eye · P` from the live decomposition (unit forward in column 3, `|col 0|` 1.1809,
  `|col 1|` 2.0994, row 3 = −eye·column) while "leaving column 2 / row 3.z alone". That required the
  reversed-Z shape to be right — still a `[hypothesis]` — and had to step around the unexplained
  per-position clip-z constant. **The one-element edit reads and writes neither**, so no assumption
  about the depth convention can affect it and no error in it can corrupt the picture. It is also
  one float instead of sixteen.
- **It works identically on the per-object path**, where `M = W · V · P` — the same single element,
  the same `d`, the same `w`. So when that path is built it needs no new derivation.
- ⚠️ **`w` MUST come from the SHARED matrix.** `|column 0|` of a per-object matrix includes the
  object's scale: a 3×-scaled object reads 3.54 where `w` is 1.18. Both harnesses assert this.
- Proof and evidence: `dev-archive/recon/2026-09-04c-one-element-stereo/` (`one_element.py`, and
  the shipped `apply_eye_offset()` exercised against independently multiplied `W`, `V`, `P` for an
  ordinary, a reversed-Z-infinite and an off-centre projection). Write-up: `modding-notes/2026-09-04c-the-per-eye-edit-is-one-float-and-a-census-tool-was-over-reporting.md`.
- **NOT established:** that it renders correctly. The algebra is proven and the write path is
  proven; only a run shows the picture.

### ⛔️ 7b. THE SHARED-MATRIX EDIT REACHES THE GPU BUT DOES NOT TRANSLATE THE WORLD (2026-09-08, `/lm`, live)

`[verified-live 2026-09-08, n=2 render states]` — and this **discharges §7a's contingency**.

`M[3][0] += d*w` on the 512-byte main-pass buffer was built, self-tested and deployed on
2026-09-04c, with the per-object branch deliberately held back as *"contingent on whether the shared
edit renders"*. **It does not render.**

**The edit fires, and `skipped=0` does not mean what it looks like.** Final counter:
`Applied 116364, skipped 0`. Reading `cbfp.c`: a buffer failing the
`slots_xyz_equal(…, 4, 9, 0.01f)` main-pass test is counted **neither applied nor skipped**. So
116,364 writes genuinely passed the discriminator and were edited; the `edited=0` outcome is out.

**The picture changes** — measured against the cleanest control available: Capture Mode freezes the
scene, and three consecutive captures differ by **exactly zero** (`mean|d|=0.0000, max 0.0`).

**But nothing translates:**

| separation | × human IPD | pixels differing >8 | best horizontal shift |
| --- | --- | --- | --- |
| 0.052 | 0.8× | 0 | 0 px |
| 1.478 | 23× | 3,181 | **0 px** |
| 13.764 | 212× | 8,735 | **0 px** |

At 13.8 **metres** of eye separation the frame does not move one pixel. What changes is **shading** —
faint intensity differences on lit surfaces. Repeated inside a live Video Mode session (animating
scene, two-shot control): control 4,061 px vs signal 7,934 px, **still 0 px of shift.**

**Three possibilities remain, and they are not equally likely:**

1. **The buffer is not the matrix that positions on-screen geometry** — leading reading; it matches
   the shading-only signature.
2. **The game re-uploads after our `Unmap`** — *weakened by our own evidence*: a full overwrite would
   leave the picture **identical**, and it demonstrably is not. Something consumes our bytes.
3. `M[3][0]` is the wrong element for this matrix's on-screen convention — not excluded here, though
   §7a's algebra was proven over 33 Python + 26 C cases.

**The observation that separates them:** read the buffer back at the next `Map` and see whether our
value survived. Small proxy change, `[PD]`.

⭐ **Consequence: the per-object `InstanceConsts` path (§6b) is now THE route, not a fallback.** Its
slots 0..3 are the full object→clip 4×4; it needs its CPU-side fill hooked. §7a's one-float algebra
carries over unchanged — only the write site moves.

### ✅ 7c. THE EDIT NOW GOES TO THE PER-OBJECT WRITE SITE (2026-09-08d, `/pd`, no launch)

`[compile-verified 2026-09-08]`, 71 offline checks against the shipped code.

§7b closed the shared branch empirically. §6b named the remaining route. The write site has moved:
`InstanceConsts` (368 bytes) is intercepted at `Map`/`Unmap` and the same one-float
`apply_eye_offset()` runs on its slots 0..3 — **handed the SHARED frame's `w`, never its own**,
because object scale multiplies column 0 (a 3× scaled object reads 3.54 where `w` is 1.18).

`NUMPAD0` selects the path: **per-object → shared → both**, defaulting to per-object. The shared
path stays reachable so the two can be A/B'd without a rebuild, and so a per-object result is never
confounded by a shared edit firing underneath it.

#### ⚠️ The load-bearing assumption — pass membership is INHERITED

Per-object buffers carry no main-pass discriminator of their own (§6b: slots 4..15 are falloff data,
not a transform). So a **latch**, set from the most recent 512-byte shared write, records whether
that write looked like the main camera (`slot4==slot9`), and per-object writes are edited only while
the latch is set **and** a `w` cached in the **same frame** is available.

**`[hypothesis]`, and the most likely thing here to be wrong.** It assumes the game interleaves
shared and per-object fills in the order the latch implies. If it does not, the symptom is specific:
**shadows and reflections swimming against a shifted eye**, because those passes got the edit too —
a different failure from "nothing moved", and the counters are what separate them.

A stale `w` is **refused, not reused**: it would be wrong by exactly the FOV change between frames,
which on screen reads as a mistuned IPD rather than a bug.

#### Scope

Only the 368-byte `InstanceConsts`. `cbInstanceConsts` exists in nine sizes from 16 to 160 bytes;
§6b says those also carry a clip transform at slots 0..3, but a 16-byte buffer cannot hold a 4×4, so
that cannot hold for every size and the population is unseparated. Widening pre-emptively would make
a bad result uninterpretable. Per-object buffers are deliberately **not** fingerprinted — one write
per draw would exhaust `FP_MAX_WRITES` (128) and `FP_MAX_BUFFERS` (8) in a single frame.

### ✅ 7d. The read-back is a STAGING COPY — reading at the next `Map` cannot work (2026-09-08d, `/pd`)

`[compile-verified 2026-09-08]`

The board asked to read the buffer back **at the next `Map`** to separate (a) wrong buffer, (b) the
game re-uploads after our `Unmap`, (c) wrong element. **That method cannot answer it.** Constant
buffers are mapped `D3D11_MAP_WRITE_DISCARD`, which by specification returns a fresh allocation whose
previous contents are **undefined** — the read would be meaningless, and meaningless in the way that
looks like data.

What works: after our `Unmap` returns and the buffer is unmapped, `CopyResource` into a `STAGING`
buffer and `Map` it `READ`.

| read-back | reading |
| --- | --- |
| our value survived | the bytes are in the buffer the game draws from; **(b) excluded**, (a) weakened, (c) survives |
| overwritten | something rewrote it after our `Unmap`; **(b) is the answer** and the edit must move later in the frame |

One-shot on `NUMPAD-DOT`/`DELETE` (four samples) because it stalls the pipeline. Uses
`real_Map`/`real_Unmap` so our own hooks cannot record a write the game never made.

### ✅ 4b. The proxy releases the real `dxgi.dll` on a dynamic unload (2026-09-08d, `/pd`)

`[compile-verified 2026-09-08]`

The proxy loaded the system `dxgi.dll` by full path and never released it. Had the game unloaded the
proxy, that copy stayed resident and the next `LoadLibrary("dxgi.dll")` **by base name** would return
it — the game would run perfectly without us, with a log ending mid-session that reads like a crash.

Released now, only when `reserved == NULL` (a genuine dynamic unload; on process exit it is
pointless). ⚠️ **Calling `FreeLibrary` from `DllMain` is against the documented loader rules and can
deadlock.** It is accepted only because this proxy already calls `LoadLibraryA` from
`DLL_PROCESS_ATTACH` — the standard proxy bargain — so the asymmetry, not the call, was the anomaly.
**If it ever deadlocks on unload, stop loading in `DllMain` too; do not reinstate the leak.**

### 🔧 Tooling: three defects found because the tooling was used (2026-09-08d, `/pd`)

`[verified-numerically 2026-09-08]`

1. **The self-test printed its verdict before a third of its own checks.** `SELFTEST PASSED` sat
   above sections 6, 7, 7b and 8, all added later — so a failure in the **stereo maths** would still
   have printed PASSED. The exit code was always right; the line a human reads was not. Moved to the
   end with a check count, and verified by deliberately breaking a late check.
2. **A pipe swallowed the suite's exit status** once it was wired into `build.sh`
   (`... | tail -1` takes `tail`'s status; `set -e` cannot help). Now captured and checked — a broken
   check makes the build exit 1.
3. **The build was not reproducible** (2 bytes, the PE `TimeDateStamp`), so "rebuild and compare the
   hash" silently could not work. `-Wl,--no-insert-timestamp` → 0 differing bytes.

⚠️ **Defect 3 is the THIRD project in one day** — `doom-2016-vr` (llvm-mingw) and `unreal-gold-vr`
(MSVC) were the others. Two toolchains, three projects: this is an estate blind spot, not a project
quirk. **Assume the hash check is broken anywhere until someone has built twice and compared.**

### ⭐⭐ 9b. VIDEO MODE: a shipped detached camera with runtime FOV control, and 157° of PLAYABLE field of view (2026-09-08, `/lm`, live)

`[verified-live 2026-09-08, n=1]`

The route, end to end: `Capture Mode → R → CAMERA SETTINGS → FIELD OF VIEW to maximum → Enter
("BEGIN SESSION") → Enter ("CONTINUE")` puts the game into **live, playable, HUD-free gameplay**.
The Capture Mode HUD bar names the key outright: `R  VIDEO MODE`.

**Measured there: `|col 0| = 0.2000` → hfov ≈ 157.4°**, via the relation fitted to §6's own two
calibration points (`hfov = 2·atan(1/|col0|)`; reproduces 58.28° and 116.91° to 0.01°).

| state | hfov |
| --- | --- |
| ordinary gameplay default | 80.48° |
| Photo-Mode Capture Mode, slider at max | 116.91° |
| **Video Mode capture session** | **≈157.4°** |

It is **not a still**: `hold w 1.5` walked Max forward with the camera following (264,354 px
changed), and the state survives the pause menu and RESUME GAME.

**The two-controller precondition is REAL, and the game states it twice in its own UI:** *"Connect a
second controller and have a friend control the camera during game play"* and *"You need to connect
a second controller … in order to capture footage that uses the capture camera."* This machine has
**zero physical pads**; two ViGEm virtual pads (`flat-to-vr-RE-toolkit/tools/hold-pads.py`) held
XInput slots [0, 1] for the session and Video Mode opened.
⚠️ **No control was run with the pads removed**, so this shows the precondition *can be satisfied
here*, NOT that the pads caused it. One `R` press with no pads is owed.

⭐ **The prize is the binding list.** The CAPTURE VIDEO panel documents what the second controller
drives, live, during gameplay: **Increase / Decrease Field Of View**, **Attach/Detach Camera To
Max**, **Toggle Game Camera**, **Toggle Camera Tracking**, Toggle Alternate Camera 1 / 2, Rotate
Camera Axis (two axes), Pan Up / Pan Down, Toggle Depth Of Field, Normal Game Speed, Slow Motion,
Start/Stop Recording.

That is a **shipped, engine-native, runtime-controllable detached camera with FOV control and an
attach/detach-to-player toggle**, reachable with no code at all — the most useful control surface
found on this game. ⚠️ **None of those buttons has been pressed.** They are `[verified-live]` as
*documentation* and `[reported]` as *behaviour* until a virtual pad drives one.

⚠️ **Unknown: how the session ends cleanly.** `Esc` reached the pause menu and `RESUME GAME`
returned *into* the session, so it is stickier than expected, and whether the 157° survives a full
exit is untested.

### ⭐⭐ 9c. THE 157° FOV PERSISTS INTO ORDINARY GAMEPLAY — an engine-native, code-free FOV lever (2026-09-08b, `/lm`, live)

`[verified-live 2026-09-08, measured numerically at three separate points]`

§9b established that a Video Mode capture session runs at hfov ≈ 157.4°. **It survives a full exit.**

```
… Video Mode → FOV to max → Enter (BEGIN SESSION) → Enter (CONTINUE)
   → Esc → Down×7 → CAPTURE MODE → Enter → Esc          ← full exit
   → ORDINARY GAMEPLAY, HUD BACK, STILL 157.38°
```

| state | `|col 0|` | hfov |
| --- | --- | --- |
| ordinary gameplay, default | 1.1809 | **80.48°** |
| Photo-Mode Capture Mode, slider at max | 0.6138 | 116.91° |
| Video Mode capture session | 0.2000 | 157.38° |
| **ordinary gameplay AFTER a full exit** | **0.2000** | **157.38°** |

Not a stale frame: Max was walked and strafed afterwards, the HUD is drawn, the scene changes, and a
fresh dump still reads `0.20000`.

**This does not contradict 2026-09-04b, it explains it.** That session measured `Esc` out of the
*still* Photo Mode restoring 80.48° at once, and was right. The carry happens only when the mode is
left via **Video Mode → BEGIN SESSION** — exactly the distinction `/gr` drew.

⚠️ **Untested: whether it survives a reload or a relaunch.** No save/config write was observed.

**Why it matters:** it is the first camera/projection lever on this project that works *and* sticks,
on a game whose shared matrix §7b has just shown we cannot move.

### ❌ 9d. The two-controller gate is DISPROVED for ENTERING Video Mode (2026-09-08b)

`[disproved 2026-09-08, n=1]` — correcting §9b's own hedge.

With XInput reporting **zero connected controllers**, verified immediately beforehand: `R` opened
Video Mode, `Enter` reached the CAPTURE VIDEO panel, and `Enter` again ran the capture session —
HUD-free, playable, 157.38°. The FRAMED claim *"Video Mode is enabled when two controllers are
connected"* is **wrong as stated for entry** on this build. §9b's two virtual pads were present but
not necessary, and the caveat recorded at the time was the whole story.

⚠️ The game's own narrower claim — a second controller is needed *"to control the camera during
game play"* — is about the bindings, not about entry, and §9e is that question.

### ⛔️ 9e. Two VIRTUAL X360 pads do not drive the second-controller camera (2026-09-08b)

`[measured 2026-09-08, 18 numeric hfov dumps + pixel deltas vs a no-input control]`

Two ViGEm pads (XInput slots [0,1]); **every** input on pad 1 exercised, each followed by a matrix
dump. **Not one changed the field of view** — `LEFT_SHOULDER`, `RIGHT_SHOULDER`, both triggers, all
four D-pad directions, both thumb clicks, `A`, `B`, `X`, `Y`: hfov read **157.38° every time.**
Pixel deltas against a 290 px control floor agreed (`A` 991, `B` 585, the rest at or below it).

**The pads moved the PLAYER instead** — the 200k–330k px deltas from sticks and shoulders were Max
walking, confirmed by resuming afterwards and finding him elsewhere in the garage. `START` opened the
pause menu, the ordinary player-one binding, which is itself evidence the game treats these pads as
**player one**.

⚠️ **This is a negative about the METHOD, not about the feature.** A game can distinguish a genuine
second device in ways a virtual pad does not reproduce, and these pads were hot-plugged *after* the
session began. Both untested. Never write this up as "the feature does not work".

**Two traps, both caught, both worth remembering:**
1. The first probe's two biggest "hits" (62× and 85× control) were the **"Controller Connected"
   toasts** drawing and clearing. Caught by looking at the frame, not the number. The re-run added an
   18 s lead-in and moved the measurement to `hfov`, which nothing drawn over the frame can perturb.
2. `START` produced a real 157.38° → 116.91° change that **means nothing** — 116.91° is exactly the
   Photo-Mode slider maximum set earlier, and the frame showed the pause menu.

### ✅ 9f. Keyboard `C` works, keyboard `X` does not (2026-09-08b)

The CAPTURE VIDEO glyph column is a **mix**: white letters `X` and `C` are keyboard keys, the
coloured circles are Xbox face buttons — matching Capture Mode's own *"press C + X"*.

- **`C`** — a large, reproducible view change with **no controller connected**: 197,887 px and
  221,173 px in two sessions, against control floors of 11,610 and 1,277.
  `[verified-live 2026-09-08, n=2]` It repositions the camera and leaves hfov at 157.38°, consistent
  with *Toggle Game Camera*. ⚠️ Not a clean symmetric toggle — second press ~11k, third ~6k, at or
  near the floor. "Switches to the game camera and stays there" is `[hypothesis]`.
- **`X`** — **nothing**: 905 px against a 1,277 px floor, i.e. *below* it, and no hfov change.
  `[disproved 2026-09-08]` as a visible effect in this dark interior.

### ⭐⭐ 6c. `V` IS A SHIPPED FIRST-PERSON COCKPIT CAMERA (2026-09-08c, `/lm`, live)

`[verified-live 2026-09-08, n=1 toggle cycle, two no-input controls]`

Blocked since 2026-09-04b for want of a drivable car; the user played through to Outer Graves and
handed back. Slot 9 is the frame-constant main camera:

| step | slot 9 (x, y, z) | movement |
| --- | --- | --- |
| base (chase) | −3295.52, 345.15, 6694.77 | — |
| **no-input control** | −3295.52, 345.15, 6694.77 | **0.00** |
| **`V` 1st press** | −3301.02, 342.94, 6691.52 | **6.76 units** |
| **`V` 2nd press** | −3295.78, 344.01, 6694.69 | **6.22 units, back** |
| no-input control 2 | −3295.83, 344.00, 6694.66 | 0.06 |

Controls at 0.00 / 0.06 against 6.76 / 6.22 in opposite directions — about a car length. **And the
frame agrees**: an interior view through the windscreen with steering wheel and dashboard, toggling
cleanly back to the chase camera.

⭐ **Why it matters:** §7b established the same day that we **cannot** move the shared matrix. `V` is
a **shipped, engine-native, keyboard-reachable first-person vehicle camera needing no code at all**
— on a driving game aimed at VR, the most valuable control surface found here. ⚠️ It gives a good
*viewpoint*, not a stereo one; per-eye projection remains §7b's unsolved problem.

⚠️ The car was **stationary throughout**. Nothing here says how the cockpit camera behaves under
motion, collision, or the game's speed-based FOV effects.

### 9g. The wide FOV is a GLOBAL persistent state — and it drifted unexplained (2026-09-08c)

`[measured 2026-09-08]` hfov read **161.08°** in the vehicle chase camera, in the vehicle
first-person cockpit, and **on foot** after stepping out — against the **80.48° default**. So §9c's
persistent state is not confined to capture mode or to a camera type, and it survived a **~1.5 hour
play session** with a region change and mission progress.

⚠️ **Recorded, not smoothed over:** the same measurement read **157.38°** earlier the same day and
**161.08°** now. The user played in between, so the change is unattributed. The qualitative claim
(roughly double the default, persistent) stands; *"the FOV you set in Video Mode is exactly what you
get later"* does **not** — something moved it.

⚠️ Still untested: survival across a **relaunch**.

### ⚠️ 10b. `keymap_group_*` in `settings.ini` is a GROUP ID, not a key code (2026-09-08c)

`keymap_group_enter_vehicle=17`, `keymap_group_exit_vehicle=17`, `keymap_group_vehicle_fp_cam=21`.
Enter and exit share `17`, which no key binding could — so the 2026-09-04 `[inferred-static]` note
that these "map vehicle_fp_cam to V and enter_vehicle to R" must not be read as coming from these
lines. Empirically on this build: **`V` toggles the cockpit camera** and **`R` exits the vehicle**,
both `[verified-live 2026-09-08]`.

**Save state:** this machine had only autosave slots 1 and 2, both in the intro — checked directly,
which is why the row stayed blocked rather than being overlooked. There is now **autosave slot 3**
(Outer Graves, *Righteous Work*, 1:36 played), so future vehicle work starts there.

### ⚠️ 10a. NumLock silently changes what the proxy's hotkeys do (2026-09-08)

With NumLock **off**, a numpad scancode produces the navigation VK (`0x51` → `VK_NEXT`), and the
proxy accepts navigation keys as aliases — but its alias table pairs them **differently** from its
numpad table. The first `numpad3` ("dump the next frame") was logged as
`cbfp: stereo separation -> 0.0520`, i.e. it ran NUMPAD9. Worse, the stereo aliases are `RIGHT` and
`UP`, which in Capture Mode **move the camera** — so an experiment could run with a drifting
viewpoint and nothing would error.

**Set NumLock ON before using the numpad hotkeys, and check the logged line names the function you
meant.** Also: six downs from `RESUME GAME` on the main menu lands on **CREDITS**; `EXIT GAME` is
the seventh.

## 7d. ⭐⭐ THE PER-OBJECT WRITE SITE IS THE ON-SCREEN TRANSFORM (2026-09-10)

Editing the per-object constant buffers **moves the world**, visibly, judged by eye against a
still scene `[verified-live 2026-09-10, n=1 session]`. The shared path was closed on 2026-09-08
(116,364 writes edited, the picture changed, the frame did not translate by one pixel even at 212x
a human IPD). This is the remaining route, and it works.

### ⚠️ First: the buffer we had been editing did not exist

`PEROBJ_SIZE` was **368**, from shader reflection (S6b named `InstanceConsts` at 368 bytes across
112 shaders). **The game never allocates a 368-byte constant buffer — not once in over 22,000
frames of gameplay** `[verified-live 2026-09-10, n=1 session]`. So the per-object edit reported
`edited=0` with **every refusal counter also 0**: not refused, never attempted.

**This dossier already contained the counter-example.** §7's `g_tracked_sizes` records that the
512-byte reflection layout has a **3136-byte RUNTIME twin**. On this engine a reflection size is
not a runtime size, and matching a buffer by a reflection-derived byte width is unsound in
general. Treat any size taken from reflection as a hypothesis about a *name*, never about an
allocation.

⭐ **What made this diagnosable was one counter per refusal reason.** "Everything zero, including
the refusals" is a different claim from "the edit was refused", and only the second would have
sent the session hunting for a latch bug. Keep that discipline.

⭐ **And the control that settled it in ninety seconds:** switch the path to SHARED (`NUMPAD0`) and
watch. `SHARED edited` climbed to 2,217 while `PER-OBJECT edited` stayed at 0
`[verified-live 2026-09-10, n=1 launch]` — proving the hotkeys land and the edit machinery works,
so the fault is specific to the per-object target. Run this before debugging anything.

### The candidate census — measure the buffer, do not guess another size

The proxy now scores every mapped constant buffer against the shape of a real object→clip matrix,
using three properties of the shared main-pass matrix already known live:

- the last **column** is not `(0,0,0,1)` — this is what rules out an affine object→world matrix,
  which is the commonest false positive;
- rows 0..2 are a bounded, non-degenerate basis;
- **row 3 is a world-scale translation** (thousands), because the camera sits thousands of units
  from the world origin. A UI or normalised-space matrix fails this.

Two mechanics are load-bearing and both were got wrong once:

1. **Sample at `Unmap`, never at `Map`.** Constant buffers are mapped `D3D11_MAP_WRITE_DISCARD`,
   so at `Map` time the contents are undefined by specification — and undefined in the most
   dangerous way, because it still looks like data.
2. **Sample in GAMEPLAY, not on first sight.** A first-sight census describes the menu and the
   loading screen. The same widths read *affine* there and *projective* in the world. The census
   therefore re-arms on the dump hotkey (`NUMPAD3`), so pressing it in gameplay re-samples
   everything against what is on screen.

### What it named

Over 300 frames of gameplay `[verified-live 2026-09-10, n=1 session]`:

| width | unmapped | object→clip-shaped | bind census |
| ---: | ---: | ---: | --- |
| **192** | 197,128 | **130,200** | `VS-b1` 75,728 + `VS-b3` 68,937 |
| **128** | 182,700 | **87,000** | `VS-b1`, `VS-b3` |
| **384** | 25,023 | 21,723 | `VS-b1` 38,410 |
| **64** | 248,475 | **20,100** | `VS-b1`, `VS-b2` |
| **96** | 104,665 | **18,000** | `VS-b1` 94,845 |
| 256, 768, 480, 624, 1392, 3792, 7632, 8112, 8208, 9024 | — | **0** | — |

The four kept show **different translations per buffer** — `(-92.4, 73.5)`, `(-108.4, 84.1)`,
`(-134.2, 71.0)` — while sharing `m[14] = 0.0992` to four decimals. Different objects, one camera.

**⭐ 384 is the camera's own viewProj, copied.** Its rows 1..3 are byte-identical to the shared
512-byte main-pass matrix (`-5789.70361, -1519.87537, 0.11118, -4465.60254`). It is deliberately
EXCLUDED from the edit: editing it would double-apply against the shared path and make any result
uninterpretable. That there are two copies of the camera matrix in different buffers is itself
worth knowing before any future stereo work.

### The result, and the two problems it hands over

Retargeted onto 192/128/96/64, with a counter per width:

```
PER-OBJECT edited=21,999,140 | refused: off-main-pass=2,828,972  no-shared-w=0  bad-matrix=0
  width 192 = 6,511,536   width 128 = 5,853,045   width 96 = 1,741,557   width 64 = 7,893,002
```

From exactly 0, and the world moves.

- **⚠️ The HUD moves with it.** §7 predicted it must not ("it does not come through this buffer").
  It does come through at least one of the four widths — the minimap and the health/weapon cluster
  slide with the scene. **Narrow it with the per-width counters, one width at a time**; `192` is
  the obvious first try, being both the top scorer and the most heavily VS-bound.
- **⚠️ A persistent smear that is not motion blur** — it survives in single-eye mode with the
  separation held still. Most likely the untested `[hypothesis]` the code already flags: per-object
  buffers carry no main-pass discriminator of their own, so pass membership is **inherited** from
  the most recent shared-buffer write (`slot 4 == slot 9`). 2,828,972 `off-main-pass` refusals say
  the latch is doing real work; the smear says not accurately enough. That calls for a better pass
  discriminator, not a different write site.

**Not established:** which width carries the HUD; whether the smear is the latch or the game's own
temporal AA reacting to a moved world; whether the shift is geometrically *correct* for a given
separation (it has been seen, never measured); and whether the copied viewProj at 384 is read by
anything that matters — it was excluded to avoid a double-apply, not shown to be inert.

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

### 9a. Capture Mode / Video Mode control surface (drained from `/gr` inbox, 2026-09-04)

**Ours, and settled:** the still Capture Mode has four tabs — CAMERA / FILTERS / CAMERA SETTINGS /
VIGNETTE — and is **mouse-only**: click the tab label, the row label, then the `<`/`>` arrows.
Keys, bar clicks and knob drags all do nothing `[verified-live 2026-09-04]`. `Esc` exits and
**restores** the default FOV at once `[verified-live 2026-09-04b, n=1]`.

**Reported, not ours — the carry-into-gameplay route** (Cole Wolfsson's Steam guide, via
`external-research/topics/2026-09-04-the-fov-carry-route-is-video-mode-and-enter-not-esc.md`):
Capture Mode → **Video Mode (`R`)** → raise FOV on the camera-settings tab → switch to the
**show HUD** tab → **`Enter`** (or gamepad `A`) to resume with the raised FOV → `V` for first
person while driving. `[reported]`

⚠️ **The step that was missing from our two failed attempts is `R`.** The "show HUD" tab lives
**inside Video Mode**, which is a different screen from the still Capture Mode whose four tabs we
enumerated — so our negative was a negative about **`Esc`**, not about the claim. On this reading
`Esc` cancels and restores while `Enter` resumes carrying the state; they are different actions.

⚠️ **A precondition that gates the whole test, and must be checked first:** the FRAMED
screenshot-community guide states that Video Mode *"is enabled when two controllers are
connected"* `[reported]`. If that holds on this build, Video Mode cannot be opened on a
keyboard-only machine at all — and two sessions of fruitless keypressing become the *expected*
outcome rather than a mystery. One pad-count check settles it before any dumping.

Two further `[reported]` details: photo mode also opens on **`X`+`C`** or the `<`/`>` keys, and the
**HUD toggle is `CAPS LOCK` or `>`**. (Note our own `[disproved]` finding in §11 that a bare `X`
does nothing — the pause page's glyphs are controller buttons.)

Each line above becomes `[verified-live]` or `[disproved]` on the next flat run.

## 10. Autonomous harness recipe (this game)
- Launch to a known scene: Steam launch → `Enter` at the title → `Enter` on RESUME GAME (main-menu
  default) → gameplay in < 45 s. Full route/hazards: `ai-game-control-profiles/profiles/mad-max.json`.
- Input: `flat-to-vr-RE-toolkit/tools/game-harness.py "Mad Max" hold <key> 0.3` — **⚠️ 70 ms taps are
  ignored on the home PC at 1920×1080; 250–300 ms holds work** `[verified-live 2026-09-04]`. Numpad
  probe keys as non-extended scancodes; arrows extended.
- Free camera: pause (`Esc`) → 7× Down (greyed rows skipped) → verify CAPTURE MODE highlighted →
  `Enter`; then arrows/WASD move, mouse rotates, `Esc` exits `[verified-live 2026-09-04]`.
- **Capture Mode's tabs and sliders are MOUSE-driven:** `game-harness.py "Mad Max" click <x> <y>` (client
  coordinates) on the tab label, then on the row label, then on the `<` / `>` arrows at the ends of the
  bar. At 784×561: CAMERA SETTINGS (452,106), FIELD OF VIEW label (85,174), its arrows (55,189) /
  (272,189). Keys, bar clicks and knob drags do nothing there `[verified-live 2026-09-04b]`.
- **Key indices in `Mad Max\settings.ini` `[KeyMapping]` are alphabetical (A=0 … Z=25):** W/A/S/D =
  22/0/18/3 (live-verified), V = 21 `vehicle_fp_cam`, R = 17 `enter_vehicle`, X = 23 `overview_camera`,
  E = 4 `action`, Q = 16 `cancel_action` `[inferred-static 2026-09-04]`. Read it before guessing a key.
- Self-close route (pause → EXIT TO MAIN MENU → confirm → 7× Down → EXIT GAME → Enter) exercised on the
  dev PC 2026-09-04b; the process was gone before a second confirm press found a window.
- Frame capture: `game-harness.py "Mad Max" shot out.png` (BitBlt); the window must be focused first or
  the grab is the whole desktop. Proxy evidence lands in `Mad Max\madmax_vr_proxy_log.txt`.

## 11. Dead ends & false leads (save future time)
- **`InstanceConsts` slots 18..21 are NOT the object's world matrix**, however 4×4-shaped they look
  in a slot census. They are a 3×4 affine applied to a *camera-relative* position and written to a
  texcoord (`o3`), in 16 shaders. Reading a register-usage table without following the
  **destination** is what makes this look like the per-object world transform.
  `[inferred-static 2026-09-04]`
- **A slot-usage census that walks back from `SV_Position` must respect program order.** Shader
  registers are reused; `r0` can feed the position early and carry something unrelated later. Our own
  `dxbc-usage.py` had this defect until 2026-09-04 and over-reported the position path by 34 rows.
  A census tool is evidence only to the extent its walk is sound — check what a listed slot's
  result is actually *written to* before believing it.

- **A constant-within-frame filter cannot see a per-pass camera** (2026-09-03c). The engine writes
  the shared buffer once per pass; the camera rows differ per pass; so the by-value probe's
  "identical across every draw in the frame" rule excluded slots 0..3 by construction and flagged
  a 4×4-shaped run (16..19) that the shaders never use as a matrix. Disassemble before designing
  the probe.
- **Capture Mode's CAMERA SETTINGS tab ignores the keyboard** (2026-09-04b): arrows/E/Tab never switch
  tabs, Down/Right never move a row or a slider, clicking the bar and dragging the knob do nothing either.
  Only clicks on the labels and on the `<` / `>` arrows work. Two sessions spent keypresses on this.
- **X is not a keyboard shortcut into Capture Mode** (2026-09-04b, n=1): the pause page's "press …"
  glyphs are controller buttons; the keymap's `overview_camera` = X does nothing in gameplay.
- **The garage car at the start of the story is a prop** (2026-09-04b, user-confirmed): no enter prompt,
  `R` does nothing. Anything vehicle-related needs a save past the first driving mission.
- **Early gotcha to remember, not yet understood (external-research, 2026-08-25, from the Helix/3DMigoto fix's writeup):** that fix requires the game's own **Depth of Field setting to be left at "normal"** — other DOF settings reportedly cause landscape depth *inversion* in stereo. The underlying cause isn't understood yet, and it's specific to 3D-Vision's technique, not confirmed to carry over to a true-VR approach — but worth testing for early rather than discovering mid-project if this engine's DOF pass turns out to interact with depth/stereo in a similarly fragile way for us.
- **Not (yet) a dead end, but a confirmed non-transferable assumption (external-research, 2026-08-25): the generic Just Cause/Apex-Engine community modding-tool ecosystem does not cover Mad Max.** apex-tools-launcher, deca, jc-model-renderer, and the Apex Resource Index all explicitly lack Mad Max support — confirmed by developer interviews to reflect a real engine divergence (§2), not just a documentation gap. Don't waste time trying these against Mad Max archives without first confirming, quickly and empirically, that they even open a file.

## 12. Open risks toward the North Star
- **Denuvo status is genuinely unresolved, not confirmed absent** (see §4) — this project's own static evidence (no "Denuvo" string, no `dbdata` activation-token file) conflicts with external community reports of it being present on Steam. Resolve with certainty the first time a debugger is attached, rather than assuming either way going in.
- Driving games carry an elevated motion-sickness risk vs. walking-sim/shooter conversions — comfort options (FOV vignette, fixed cockpit reference frame, etc.) are likely to matter more here than in other projects, same as the Burnout Paradise front.
- Racing/open-world HUD complexity (speedometer, minimap, mission markers) may need special handling to stay legible and comfortable in a headset — worth cross-referencing against the community FOV mods' "HUD removal" toggles as a starting point.
