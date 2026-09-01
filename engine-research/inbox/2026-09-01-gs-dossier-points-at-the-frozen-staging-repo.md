# Dossier §line 35 points at `mad-max-vr-staging`, a frozen pre-consolidation repo

Filed by: `/gs`, 2026-09-01

`engine-research/ENGINE-DOSSIER.md:35` cites the deployed proxy as:

```
deployed `mad-max-vr-staging/proxy-dxgi/`'s `dxgi.dll` to the game folder
```

Since the 2026-08-30 consolidation the private staging monorepo is one repo with a folder per
game, so the live path is **`staging/mad-max-vr/proxy-dxgi/`**. `mad-max-vr-staging` still
exists as a **frozen duplicate** pending the user-approved deletion pass
(`claude-memory/consolidation-2026-08-30.md`), so the old name resolves — to stale content
that must never be pushed to. That is worse than a broken link: it fails silently.

This matters more than the other stale references in the estate because the line names **where
a live-verified, working DLL lives**. It is the first thing a session would follow to redeploy.

`[verified 2026-09-01]` — read from the file; `staging/mad-max-vr/` confirmed present in the
staging clone.

## Suggested fix (modding lane owns the dossier)

`mad-max-vr-staging/proxy-dxgi/` → `staging/mad-max-vr/proxy-dxgi/`.

Same class of drift, same repo, lower stakes: line 28's surrounding text is fine — only the
staging path needs touching.
