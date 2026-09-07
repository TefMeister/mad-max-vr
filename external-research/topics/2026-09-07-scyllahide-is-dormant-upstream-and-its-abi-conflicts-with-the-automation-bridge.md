# ScyllaHide is dormant upstream — and wanting it back means giving up the automation bridge

**Status:** 🆕 new · **Priority:** medium — it does not reopen a dead end; it **closes** one properly,
and records a constraint on the only remaining route that nobody has written down.

## The claim this checks

This project's dossier, 2026-08-25, with the mechanism verified by `objdump`:

> **ScyllaHide tried (2026-08-25), genuine plugin-ABI incompatibility, not a config error** …
> `Export "pluginit" not found in plugin: ScyllaHideTEPluginx64`. ScyllaHide's plugin exports
> `TitanDebuggingCallBack`/`TitanRegisterPlugin` — an older, legacy x64dbg plugin ABI — while the
> currently-installed x64dbg build (and `x64dbg-automate`, which loads correctly) expects the modern
> `pluginit`/`plugsetup`/`plugstop` interface. … would need either **an older x64dbg build matching
> ScyllaHide's expected ABI**, or **a rebuild of ScyllaHide against the current SDK**; neither pursued.

`manhunt-2003-vr` propagates it as a **portfolio-wide** dead end with *"don't re-attempt without a
version change to x64dbg itself"*, and `burnout-paradise-vr`'s dossier still carries a **plan that
depends on ScyllaHide** — *"load the ScyllaHide x64dbg plugin … before assuming Denuvo blocks attach
outright."*

A "don't re-attempt until upstream moves" claim is exactly the kind that should be re-checked rather
than inherited, so this pass checked it.

## ✅ The dead end stands — and it is now known to be *stable*, not merely current

Read from GitHub's API, not from a search summary `[verified-live 2026-09-07, n=1 API read]`:

| fact | value |
| --- | --- |
| latest release | **v1.4, published 2023-03-24** |
| any release since | **none** — the next-newest are 2021 snapshots |
| last commit on `master` | **2023-07-29** |
| repository `pushed_at` | 2024-06-04 (not `master`) |
| archived? | **no** — open, with **53 open issues** |

So the dossier's *"last released 2023-03-24"* is **still accurate today**, roughly two and a half
years on. The project is not archived, but `master` has been untouched for over two years.

**What that changes:** *"don't re-attempt without a version change"* stops being an open watch and
becomes a **settled** state. Waiting for an upstream ScyllaHide release is not a realistic unblock,
and nobody should re-check this for a good while. Of the dossier's two named routes, **the "rebuild
against the current SDK" one has no upstream momentum behind it** — 53 open issues and a dormant
master mean it would be our work, not someone else's.

## ⚠️ The constraint nobody has recorded: the two plugins want **opposite** x64dbg ABIs

This follows directly from the dossier's own evidence but is not stated anywhere:

- **ScyllaHide** exports the **legacy** `TitanRegisterPlugin` interface → it needs an **older**
  x64dbg.
- **`x64dbg-automate`** — the MCP automation bridge this estate drives the debugger with — targets the
  **modern** `pluginit` interface, and the dossier explicitly notes it *"loads correctly"* against the
  current build.

**So the remaining viable route — downgrade x64dbg to match ScyllaHide — would break the automation
bridge.** You can have anti-anti-debug **or** scripted debugging on a given install, not both.
`[inferred-static 2026-09-07]` — a direct consequence of the two recorded export sets, not something
observed.

That matters most for **`burnout-paradise-vr`**, whose recorded plan is to reach for ScyllaHide
against Denuvo. That plan is not just blocked; if it were unblocked by downgrading, it would cost the
tooling every other project uses.

## ⭐ And the machine is already half-way to the right answer

Two x64dbg installs exist on this machine, and they are provisioned differently
`[measured 2026-09-07]`:

| install | x64dbg build | ScyllaHide | `x64dbg-automate` |
| --- | --- | --- | --- |
| WinGet package | 0.0.2.5 (2026-05-27) | present, both bitnesses (2026-08-25) | present, both bitnesses (2026-08-25) |
| `AppData\Local\x64dbg` | 0.0.2.5 (2026-05-27) | **absent** | x64 only, older (2026-07-27) |

**Two installs is the correct architecture for this constraint** — one pinned to an old build for
ScyllaHide, one current for the automation bridge — and the machine already has two, apparently by
accident rather than design. Making that deliberate is cheaper than choosing between the two
capabilities.

⚠️ Note the ScyllaHide files in the WinGet copy are dated the same day as the incompatibility finding,
and both bitnesses carry a **zero-byte `scylla_hide.log`**. **A zero-byte log is consistent with the
plugin failing at load, not with it working** — a plugin that never reaches `pluginit` writes nothing.
I initially read the files' presence as evidence it might work; the dossier's `objdump` evidence is
stronger and it says otherwise.

## What I checked and did NOT find

- **No fork with a modern-ABI rebuild.** Several ScyllaHide forks exist, but the ones surfaced are
  plain mirrors of the same upstream, not ports to the `pluginit` interface `[reported 2026-09-07]`.
  ⚠️ This was a search-result-level check, not an exhaustive fork audit — recorded as "none surfaced",
  not "none exists".

## The concrete next steps

None urgent, and deliberately so:

1. **Record the dead end as settled** rather than pending, with the API-read dates above, so nobody
   re-checks upstream for a while.
2. **Add the ABI conflict** to the dossier beside the two named routes, because it removes the
   cheaper of them as a free option.
3. **If ScyllaHide is ever genuinely needed** (realistically: `burnout-paradise-vr` vs Denuvo), the
   route is a **second, pinned-old x64dbg install** kept separate from the automation one — not a
   downgrade of the working install.

## Sources and credit

- **x64dbg / ScyllaHide** — mrexodia, NtQuery and the ScyllaHide contributors:
  <https://github.com/x64dbg/ScyllaHide>. Release and commit dates read via the GitHub API
  `[verified-live 2026-09-07]`.
- **`x64dbg-automate`** — dariushoule: the modern-ABI plugin whose correct loading is what makes the
  conflict concrete.
- This project's own `ENGINE-DOSSIER.md` (the 2026-08-25 `objdump` finding),
  `manhunt-2003-vr`'s dossier (the portfolio-wide propagation) and `burnout-paradise-vr`'s dossier
  (the dependent plan).

## Method note

The first search returned summarizer prose saying "last push June 4 2024" with no release detail. Per
this lane's own rule — *a claim that appears only in summarizer prose is not `[reported]`* — it was
re-checked against the GitHub API, which is where every date above comes from. The summary was not
wrong, but it was not evidence either, and it omitted the release history that actually answers the
question.
