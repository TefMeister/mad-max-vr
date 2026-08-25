# MMConsole: a community tool already unlocks the exact developer console system our own static recon found

**Status:** 🆕 new · **Priority:** high — directly answers `ENGINE-DOSSIER.md` §9's open question
("how it's opened in-game is not yet confirmed") and adds relevant evidence to §4's Denuvo question.

## Why this is an exact match

The modding session's own M0 static recon (2026-08-25) found a real internal developer-console
system in `MadMax.exe` — an `IConsoleCommand` class and literal help text naming `invoke`, `set`,
`get`, `variable_list`, `function_list` — but flagged "how it's opened in-game is not yet confirmed"
as an open question for the first live session. This search pass found a community tool that has
already solved exactly that problem.

## What MMConsole is

**MMConsole** (distributed via Nexus Mods, "command console" mod for Mad Max) works by **injecting a
thread into the running game process**, then accepting console commands either typed live into its
own separate console window or fed from a batch file — designed so commands can be scripted or bound
to hotkeys/macro devices (keyboard, a spare controller, a Stream Deck). Workflow: launch the game
normally first, then separately launch `MMConsole.exe`, which attaches and exposes the command
interface. Per its own compatibility notes, it explicitly supports:
- **Steam: console** (command execution only)
- **GOG: console, dumper**
- **Origin: console, dumper**

## Why the Steam-vs-GOG/Origin feature gap is itself a useful data point

MMConsole offers a **"dumper" feature on GOG and Origin but not on Steam**. Memory/executable dumping
tools are a class of tool Denuvo-style anti-tamper protection specifically targets and degrades
(the whole point of Denuvo's virtualization/encryption is to make a clean memory dump of the real
code difficult while it's "wrapped"). A third-party tool author drawing exactly this Steam-vs-other-
storefronts capability line is *circumstantial but real* corroborating evidence that something
Denuvo-shaped is specifically present on the Steam build and specifically absent on GOG/Origin —
consistent with, and adding independent weight to, the external community reports already recorded
in `ENGINE-DOSSIER.md` §4 (and in tension with this project's own "no `Denuvo` string found"
static-analysis result, which remains genuinely unresolved). This isn't proof either way, but it's a
second independent signal pointing the same direction as the community reports, worth weighing
alongside the static evidence rather than deferred to it alone.

## Why this matters for the mod itself

- **Confirms the internal console system found statically is real, live-reachable, and already
  unlocked by a third party against the Steam build specifically** — the "console" capability is
  listed for Steam too, just without the dumper. That means thread injection + console command
  execution is already a demonstrated-working technique against this exact target, independent of
  whatever the ultimate Denuvo answer turns out to be.
- `variable_list` / `function_list` (already known from static strings) run through MMConsole would
  self-document the entire cvar/console surface live — exactly the "worth running first live" plan
  already noted in §9 — this tool may be the fastest way to actually do that, rather than building an
  injector from scratch just to reach the console.

## Concrete next step

When live investigation resumes, treat MMConsole as a candidate fast-path to actually exercise the
already-known console system (`invoke`/`set`/`get`/`variable_list`/`function_list`) and self-document
§9's cheat sheet, before or alongside building this project's own from-scratch DXGI-proxy-based
tooling. As always, don't copy MMConsole's own code/binary into this project — use it as an external
tool to observe behavior, same as Cheat Engine, and reimplement anything needed independently.

## Sources

- https://www.nexusmods.com/madmax/mods/43
