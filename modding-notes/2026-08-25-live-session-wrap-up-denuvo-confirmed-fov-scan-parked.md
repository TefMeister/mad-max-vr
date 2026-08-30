# 2026-08-25 — First live session: Denuvo confirmed for real, FOV hunt parked

Wrapping up today's live session in plain terms.

## What actually happened, in order

1. **The proxy DLL just works.** Deployed `dxgi.dll` to the game folder, launched normally —
   no issues, no crashes, nothing weird. The log showed exactly what we expected: the game
   calling `CreateDXGIFactory1` for a real `IDXGIFactory1`. First try, clean.
2. **We got debugger tooling working from scratch.** The x64dbg MCP integration needed a
   plugin that wasn't installed (`x64dbg-automate`) — downloaded and installed it with the
   user's go-ahead. Also tried ScyllaHide (the standard "anti-anti-debug" tool) but it turned
   out to be built for an older, incompatible version of x64dbg's plugin interface — a real
   dead end with that specific tool, not something to keep pushing on.
3. **Denuvo is definitely active on this build.** Tried attaching a debugger to the running
   game three separate times (once non-elevated, twice fully elevated as Administrator, on
   two different game launches) — every single attempt was refused with the same error. This
   settles the question our static file analysis couldn't: something (almost certainly
   Denuvo) is actively blocking external debuggers from reaching in.
4. **That doesn't actually threaten the mod.** Our proxy DLL, ReShade, Special K, and vorpX
   all get their code running *inside* the game through the normal way Windows loads DLLs —
   none of them need the kind of external access a debugger uses. That's exactly why they all
   keep working under Denuvo while `x64dbg attach` doesn't.
5. **Tried to read the FOV slider value from memory, using our own proxy DLL's in-process
   access instead of a blocked external debugger.** Worked technically (the scan ran, the
   hotkeys worked once we fixed a NumLock quirk), but the results were too noisy to actually
   identify the real FOV variable — thousands of matches, many clearly unrelated data that
   happened to fall in the same number range. **Parked, not solved** — this was curiosity, not
   something the actual VR work needs yet.

## Where things stand

Nothing here changes the plan. The injection foothold is proven live. The renderer is
understood. The camera/projection question (the real "does this become VR" question) still
needs proper shader-reflection work down the line — the FOV memory-scan attempt was a
shortcut worth trying, not the real path, and its inconclusive result doesn't set anything
back.

Full technical detail: `mad-max-vr-engine-research`, `ENGINE-DOSSIER.md` §4.
