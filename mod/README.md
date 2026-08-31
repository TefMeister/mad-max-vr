# Mad Max VR

A VR conversion mod for **Mad Max** (2015, Avalanche Studios) — the goal is
stereo rendering and 6DOF head tracking, with motion-controlled aim/driving
input to follow once the core render path is proven out.

> **Status: work in progress — nothing playable released yet, no code written
> yet.** This folder holds releases only; watch it if you want to
> know the moment there is something to try.

## What this will be

Mad Max runs on Avalanche Studios' proprietary in-house engine (the same
lineage that powers the *Just Cause* series), rendering a large open world.
The concrete injection/hooking approach hasn't been determined yet — that is
the first job of engine research, tracked in
[`engine-research/`](../engine-research/).
As with our other conversions, the playable mod is almost the by-product: the
real goal is the knowledge gained on the way there, written down and shared
so anyone can do the same for any game — see the engine dossier above and the
cross-engine
[flat-to-VR library](https://github.com/TefMeister/flat-to-vr-cross-engine-research).

## What you will need

- Your own legitimate copy of **Mad Max** (this mod contains **no** game
  files).
- A PC VR headset (target runtime TBD — likely SteamVR, possibly OpenXR).

## The folders for Mad Max VR

Everything for this game lives in one repository, one folder per job — so you
always know where to look. You are in **`mod/`**.

| Folder | What lives here |
| --- | --- |
| **`mod/`** ← you are here | The mod itself — currently empty; groundwork phase. |
| [`dev-archive/`](../dev-archive/) | Full development history — snapshots, probes, dead ends, raw recon. |
| [`modding-notes/`](../modding-notes/) | Readable field notes / progress ledger. |
| [staging/mad-max-vr](https://github.com/TefMeister/staging/tree/main/mad-max-vr) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| [`engine-research/`](../engine-research/) | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [`external-research/`](../external-research/) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Credits, scope, and legality

Non-commercial fan project; requires an owned copy; redistributes no original
assets. We credit everyone whose work this builds on — see
[`CREDITS.md`](CREDITS.md) — and we honour correction/removal requests from
rights holders promptly.

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
