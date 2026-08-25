# M0 static recon — 2026-08-25

Pure file-based static analysis of the installed `MadMax.exe` — no process was launched or
attached to. Tools: `file`, `objdump`/`strings` (llvm-mingw, x86_64 target since this exe is
64-bit — a different toolchain invocation than Burnout Paradise's 32-bit target).

## PE header (`objdump -p`)
```
file format coff-x86-64
Characteristics 0x23: relocations stripped, executable, large address aware
Time/Date: Thu Oct 22 11:54:32 2015
Magic: 020b (PE32+, i.e. 64-bit)
AddressOfEntryPoint: 0x1b36728
SizeOfImage: 0x5d88000 (~93.5 MB)
Subsystem: Windows GUI
```
73.3 MB on disk. Entry point RVA lands inside the small `.xcode` section (~6 KB), not the
huge `.xpdata` blob — different shape from Burnout Paradise, where the entry point sat
*inside* the giant opaque section.

## Section table
```
Idx Name          Size     VMA              Type
  0 .bss          00000000 0000000140001000 BSS
  1 .data1        00569200 0000000141228000
  2 .data         0005e000 0000000141792000
  3 .pdata         00125600 0000000141a0c000
  4 .reloc        00001200 0000000141b32000
  5 .trace        00000286 0000000141b34000 TEXT   <- tiny, 646 bytes
  6 .xcode        0000176c 0000000141b35000 TEXT, DATA  <- entry point is here
  7 .sbss         00001000 0000000141b37000
  8 .xpdata       0421c000 0000000141b38000 DATA   <- ~69.9 MB, marked DATA not TEXT
  9 .xtext        0003321c 0000000145d54000 DATA
```
Non-standard section names (no `.text`/`.rdata` at all), but `.xpdata` being DATA-typed
(not executable) and the entry point sitting in a small named section rather than inside the
giant blob makes this look less like an active Denuvo VM wrapper than Burnout Paradise's
structure — read as circumstantial, not conclusive, alongside the direct evidence below.

## Import table (`DLL Name` entries — much fuller than Burnout Paradise's near-empty one)
```
ADVAPI32.dll, DINPUT8.dll, GDI32.dll, HID.DLL, KERNEL32.dll, MSVCP100.dll, MSVCR100.dll,
OLEAUT32.dll, SETUPAPI.dll, SHELL32.dll, SHLWAPI.dll, USER32.dll, VERSION.dll, WINHTTP.dll,
WININET.dll, WINMM.dll, WS2_32.dll, WSOCK32.dll, XINPUT9_1_0.dll, bink2w64.dll, d3d11.dll,
d3d9.dll, dxgi.dll, fmod_event64.dll, fmodex64.dll, ole32.dll, steam_api64.dll
```
`steam_api64.dll` is a direct static import here (unlike Burnout Paradise) — Steamworks is
genuinely built into the exe, no separate launcher handoff expected.

## Renderer strings
```
D3D11CreateDevice
CreateDXGIFactory1   <- the specific DXGI entry point actually called (not plain CreateDXGIFactory)
d3d11.dll / d3d9.dll / dxgi.dll (import names)
```

## Engine identification strings
```
Avalanche Engine
Ai.AvalancheFuryRoad / Animation.AvalancheFuryRoad / Physics_2012.AvalancheFuryRoad
D:\dev\depot\Other\DevRel\Clients\Avalanche\2013_2\Source\Common/Internal/GeometryProcessing/Triangulator/hkgpTriangulator.inl
Havok StackTracer / HavokWorkerThread / Havok version: %s
```

## Console/cvar system
```
.?AVIConsoleCommand@Base@@
"...console commands: 'invoke', 'set', 'get', 'variable_list', 'function_list'"
```
Real developer console class + help text confirmed present in the binary.

## Anti-cheat / DRM string search — all negative except the Denuvo question itself
```
battleye / easyanticheat / EAC.dll / securom / safedisc / link2ea -> no hits
"Denuvo" (any case) -> ZERO hits anywhere in the binary
```
Cross-checked against the specific file external-research named as Denuvo's offline
activation-token location: `Steam\userdata\859147959\234140\` contains only
`GameSave01.sav`, `GameSave02.sav`, `Settings.sav`, `remotecache.vdf` (all ordinary Steam
cloud-save files) — **no `dbdata` file exists**. See `ENGINE-DOSSIER.md` §4 for the full
reasoning on why this conflicts with external-research's community-sourced Denuvo claim, and
the working hypothesis (later patch removed it) — recorded as genuinely unresolved, not
settled either way.

## What this means for the project

Best-evidenced feasibility case in this portfolio so far, before any of our own live testing:
D3D11-only renderer (developer-confirmed), a real console/cvar system, and — per
external-research — four independent third-party tools (vorpX, ReShade, Special K, a mature
Cheat Engine AOB table) already work against this exact build, one of which (the CE table)
has a directly-callable "change camera" function. Full synthesis in `ENGINE-DOSSIER.md`.
