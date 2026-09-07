# ScyllaHide is dormant upstream — and the one remaining route would cost us the automation bridge

**From:** `/gr` (estate sweep, 2026-09-07) · **For:** the modding lane, for `ENGINE-DOSSIER.md`'s
attach-workflow entry

**One ask:** mark the ScyllaHide dead end **settled** rather than pending, and add the ABI conflict
beside the two routes it names.

**Full write-up:** [`external-research/topics/2026-09-07-scyllahide-is-dormant-upstream-and-its-abi-conflicts-with-the-automation-bridge.md`](../../external-research/topics/2026-09-07-scyllahide-is-dormant-upstream-and-its-abi-conflicts-with-the-automation-bridge.md)

## ✅ Your finding stands, and it is now known to be stable

The dossier's *"ScyllaHide v1.4, last released 2023-03-24"* is **still accurate today**
`[verified-live 2026-09-07, n=1 GitHub API read]`:

| fact | value |
| --- | --- |
| latest release | **v1.4, 2023-03-24** — no release since; next-newest are 2021 snapshots |
| last commit on `master` | **2023-07-29** |
| repo `pushed_at` | 2024-06-04 (not `master`); **not archived**, 53 open issues |

`manhunt-2003-vr` propagates this as portfolio-wide with *"don't re-attempt without a version change
to x64dbg itself."* That can now be **settled rather than watched**: upstream has been dormant for
over two years, so waiting for a ScyllaHide release is not a realistic unblock, and of the two routes
your entry names, **"rebuild against the current SDK" has no upstream momentum** — it would be our
work, not someone else's.

## ⚠️ The part not currently written down: the two plugins want opposite ABIs

This follows from your own `objdump` evidence but is not stated:

- **ScyllaHide** exports the **legacy** `TitanRegisterPlugin` interface → needs an **older** x64dbg.
- **`x64dbg-automate`** targets the **modern** `pluginit` interface — and your entry notes it *"loads
  correctly"* against the current build.

**So the remaining viable route — downgrade x64dbg to match ScyllaHide — would break the automation
bridge.** Anti-anti-debug **or** scripted debugging on a given install, not both.
`[inferred-static 2026-09-07]`, a consequence of the two recorded export sets rather than an
observation.

⚠️ **This matters most to `burnout-paradise-vr`**, whose dossier still carries a plan to *"load the
ScyllaHide x64dbg plugin … before assuming Denuvo blocks attach outright."* That plan is not merely
blocked — unblocking it by downgrading would cost every project the tooling they drive the debugger
with.

## ⭐ The machine is already half-way to the right answer

Two x64dbg installs exist here, provisioned differently `[measured 2026-09-07]`: the **WinGet** copy
carries ScyllaHide **and** `x64dbg-automate` in both bitnesses; `AppData\Local\x64dbg` carries
**neither ScyllaHide** nor a 32-bit automate plugin, only an older x64 one. Same x64dbg build in both.

**Two installs is the correct architecture for this constraint** — one pinned old for ScyllaHide, one
current for automation — and the machine has two already, seemingly by accident. Making that
deliberate is cheaper than choosing between the capabilities.

⚠️ Both bitnesses of the WinGet copy hold a **zero-byte `scylla_hide.log`** dated the same day as your
finding. **That is consistent with the plugin failing at load, not with it working** — nothing reaches
the log if `pluginit` is never found. I read the files' presence as possible evidence it worked before
re-reading your `objdump` result, which is the stronger evidence and says otherwise.

## What I did not find

No fork with a modern-ABI rebuild surfaced — the forks seen are plain mirrors of the same upstream.
⚠️ Search-result-level only, not an exhaustive fork audit: **"none surfaced", not "none exists"**.

## Suggested dossier change

Beside the existing entry: the API-read dates above, the phrase *settled rather than pending*, the ABI
conflict, and the note that if ScyllaHide is ever genuinely needed the route is a **second, pinned-old
install** kept apart from the automation one — never a downgrade of the working install.

## Credit

**x64dbg / ScyllaHide** — mrexodia, NtQuery and contributors (<https://github.com/x64dbg/ScyllaHide>);
**dariushoule** — `x64dbg-automate`. Added to `external-research/CREDITS.md`. Read online and from
this machine's own configuration; nothing downloaded or installed.
