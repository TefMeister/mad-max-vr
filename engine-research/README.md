# Mad Max (2015) — VR Engine Research

Engine research toward a VR conversion of **Mad Max** (2015, Avalanche
Studios) — stereo rendering, 6DOF head tracking, and motion-controlled input
as the goal.

This repository holds two things:

- **[`PLAYBOOK.md`](PLAYBOOK.md)** — a reusable, engine-agnostic, point-by-point
  method for taking *any* game whose engine nobody has converted to VR and
  getting it there. It is oriented around one North Star: **the game rendering
  in a headset with head tracking**, with everything else built on top. The same
  playbook is copied into each of our VR projects' research repos.
- **[`ENGINE-DOSSIER.md`](ENGINE-DOSSIER.md)** — the distilled, current-truth
  reference for *this* game's engine. Currently just the identity section —
  engine research on Mad Max has not started yet.

The blow-by-blow development history lives in the sibling repositories
(`-dev-archive` for the messy in-progress record, `-modding-notes` for readable
field notes). This repo is the consolidated engine knowledge, not the diary.

## The six repositories for Mad Max VR

Everything for this game lives in six repositories, each with one job — so you
always know where to look. You are in **mad-max-vr-engine-research**.

| Repository | What lives here |
| --- | --- |
| [mad-max-vr-mod](https://github.com/TefMeister/mad-max-vr-mod) | The mod itself — currently empty; groundwork phase. |
| [mad-max-vr-dev-archive](https://github.com/TefMeister/mad-max-vr-dev-archive) | Full development history — snapshots, probes, dead ends, raw recon. |
| [mad-max-vr-modding-notes](https://github.com/TefMeister/mad-max-vr-modding-notes) | Readable field notes / progress ledger. |
| [mad-max-vr-staging](https://github.com/TefMeister/mad-max-vr-staging) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| **mad-max-vr-engine-research** ← you are here | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [mad-max-vr-external-research](https://github.com/TefMeister/mad-max-vr-external-research) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Status

Project started 2026-08-25. Groundwork phase: repos created, no engine
research done yet. See the dossier for the current phase and open risks as
they're filled in.

## Scope, ethics, and legality

- This is a **non-commercial fan project**. It requires owning a legitimate copy
  of the game and **redistributes no original game assets** — only files we
  create. See [`.gitignore`](.gitignore).
- We **credit everyone** whose work or research this builds on, and we honour
  correction/removal requests from actual rights holders. See
  [`CREDITS.md`](CREDITS.md).

## Templates

New engine? Start its dossier from
[`templates/per-engine-research-template.md`](templates/per-engine-research-template.md).

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
