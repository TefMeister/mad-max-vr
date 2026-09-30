# The dossier still says the smear is "not motion blur" (line ~784)

Supersedes: engine-research/ENGINE-DOSSIER.md, the bullet "A persistent smear that is not motion blur" (about line 784)

From: /gs, 2026-09-30.

The 2026-09-30 `/lm` pass showed the smear IS motion blur: with `MotionBlur=0` in `settings.ini` the car and
the crate wall are sharp, same build and separation `[verified-live 2026-09-30, n=1]`. The dossier's own new
section at the end ("2026-09-30: the HUD skip and the motion-blur smear") says so, but the older bullet near
line 784 still states the opposite without a correction note, so a reader who stops there gets the wrong
answer.

Fix (modding lane): mark the old bullet `[disproved 2026-09-30]` and point it at the new section. The
2026-09-10 modding-notes entry is a dated record and can stay as written.
