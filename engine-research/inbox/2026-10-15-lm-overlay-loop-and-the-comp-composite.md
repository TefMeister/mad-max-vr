# 2026-10-15 (`/lm` reader, no launch): the Steam overlay loop, and the composite that has no depth of field

## 1. Why the overlay loops, and the fix (staging `54f7eaa`, build `557005ddf491`)

- The loop: game Present -> our vtable `hk_Present` -> the real Present (dxgi.dll+0x18c0, starts `e9`, the overlay's
  jump) -> the overlay -> back through the vtable slot (ours) -> the real Present -> ... The guard cut it at depth 5,
  but no level ever reached the real function's body, so nothing was presented: black window, Present storm
  `[verified-live 2026-10-15, n=1]` (the guarded-run log), mechanism `[inferred-static 2026-10-15]`.
- Genuine `CDXGISwapChain::Present` (dxgi.dll 10.0.19045, RVA 0x18c0) makes only direct calls, never back through the
  vtable `[inferred-static 2026-10-15]`; its first instruction is `mov [rsp+10h], rbx`, exactly 5 bytes, so the
  overlay's 5-byte jump covers one whole instruction.
- The fix: a nested Present goes to a **pre-overlay Present**: a trampoline built from dxgi.dll's own bytes on disk
  (whole, position-independent instructions covering every byte the overlay changed, then a jump back into the live
  function). The outer call still goes through the overlay, so its picture is drawn once and the frame is presented
  once. Built on the first nested call; refuses (and keeps the old guard) on an RIP-relative or unknown instruction,
  a patch wider than 16 bytes, or a file whose link stamp differs from the loaded module. Switch: `madmax_vr.ini`
  `[present] overlay_fix=0`. Self-test runs a real trampoline on a fake patched function `[compile-verified 2026-10-15]`.
- Log lines to read on the next Steam-launched bridge run: `first nested Present; the real Present's jump goes to
  <module>; our hk_Present starts xx xx`, `pre-overlay Present BUILT - 5 byte(s) patched, 5 copied`, `N nested
  Present(s) sent to the pre-overlay Present`, and no `Present STORM`.

### Why only with the bridge, and only from the Steam launcher `[hypothesis]`

The overlay's code calls the vtable's Present slot as "the original" - which only loops if it read that slot after
we put `hk_Present` there. The re-entries begin at the instant the simulator's session starts (13:46:55.492, right
after the headset device and its swapchains appear) `[measured 2026-10-15, n=1]`, so the most likely reading is that
the overlay re-hooks when another device/swapchain appears in the process and picks our pointer up from the shared
vtable. Started directly (SteamAPI_Init loads the overlay later and it logs only the game's one swapchain), it does
not happen (n=2). Two alternatives remain: our own route-B throwaway swapchain (not created on these runs: route A
fired), or the launcher-injected overlay hooking `dxgi` before our proxy is loaded. What separates them: Steam's
`logs\gameoverlay_renderer.txt` from a launcher + bridge run (a second `Hooking vtable for swap chain` / `Tracking new
swap chain` at session start = re-hook), and the new log line naming where the jump goes and whether `hk_Present`
itself was patched. Steam keeps only the last two runs in that log; the 13:46 run is already gone.

Odd and unexplained: `gameoverlayrenderer64.dll+0x93f6f` (the logged return address) lands mid-instruction in the
DLL on disk today (link stamp 2026-10-13, no Steam update since) `[measured 2026-10-15]`, so the call site could not
be read statically.

## 2. The cockpit near blur is not in the last pass (staging `864d0dc`, build `909a4e0a18cb`)

- `MadMax.exe` names three composite families, `Dof_*`, `DofBokeh_*` and **`Comp_*`** (plus `TMOnly_*`). The shipped
  `comp_*` (24 variants) samples only the scene, bloom, secondary bloom, lens dirt and the colour grade: no depth, no
  blurred copy `[inferred-static 2026-10-15]`. With `HQDof=0` and `PostEffects=0`, `dof_*` and `dofbokeh_*` drew 0
  times `[verified-live 2026-10-15, n=1]`, so the composite in use is almost certainly `comp_*` `[hypothesis]`, and
  the wheel's softness is already in the scene picture or is not a post effect at all.
- `comp_*` reads `cbConsts` c0.x (fringe, `_ca` only), c1, c2.x, c3.x/y (bloom), c9, c10.x, c12.w (lens dirt): the
  dof edit is safe on it and now zeroes its lens dirt and fringe too.
- New tool: the census line `cbfp pass frame=N: <pass>=<draws> ...` for 121 shipped full-screen pixel-shader passes,
  and `madmax_vr_skip.txt` (names, `prefix*`) to leave passes out. Next run: chase camera, then cockpit; passes that
  only the cockpit draws are the suspects; skip them one at a time and look at the wheel.
- If no extra pass shows up: compare edges in a cockpit screenshot. A post blur softens the wheel's outline against
  the window; low texture detail (`TextureDetail=1` in settings.ini) leaves outlines sharp and only the surfaces
  mushy. `Bloom=1` also lays a soft glow over a dark interior.
