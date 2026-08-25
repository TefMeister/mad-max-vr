# Denuvo-on-Steam question: more recent community evidence leans toward "still present," not resolved

**Status:** 🆕 new · **Priority:** high — directly follows up `ENGINE-DOSSIER.md` §4/§12's flagged
"genuinely unresolved" Denuvo question with more recent, more specific evidence. Does not settle it
with certainty — that still requires a live debugger attach, as the dossier already says — but adds
real weight to one side.

## Why this follow-up exists

The modding session's own M0 static recon found **no** `"Denuvo"` string anywhere in `MadMax.exe`
and **no** `dbdata` activation-token file in the expected Steam userdata path, which conflicts with
external-research's earlier report (from the previous sweep) that the Steam build is Denuvo-
protected. The dossier honestly recorded this as unresolved and floated a hypothesis: maybe this
specific, currently-installed (auto-updated) build had Denuvo quietly removed in a later patch,
mirroring the industry-wide "ship with Denuvo, strip it later" pattern this portfolio already
documented for Burnout Paradise.

## What a more targeted search found

Checking Steam discussion threads specifically for **recency** (not just topic) turned up posts as
recent as **very late December 2024 / early January 2025** — about 20 months before this research
session, and meaningfully closer to "current" than the older threads the first pass's search
surfaced:

- *"AFAIR its still present in steam version"* (Dec 31, 2024)
- A player reporting a real, measured **performance difference between storefront versions**:
  *"steam version ran 15% slower at 4k than gog version. refunded steam, kept gog"* (Jan 3, 2025) —
  notable because Denuvo's characteristic behavior is exactly this kind of storefront-specific
  performance overhead; a bare "still has Denuvo" claim could be mistaken, but a *specific,
  independently-motivated performance complaint* pointing the same direction is more convincing.
- No thread found (in this pass or the previous one) reporting an actual removal patch, changelog
  entry, or "it's gone now" confirmation at any date.

Separately, the companion **MMConsole topic** (this same sweep) found a third-party tool drawing a
Steam-vs-GOG/Origin capability line (dumper support absent specifically on Steam) that independently
points the same direction.

## What this means for the open question

This doesn't overturn the modding session's own direct static evidence (zero `"Denuvo"` string hits,
missing `dbdata` file are real, first-party observations against the actually-installed exe) — but
it does mean the "maybe it was quietly removed" hypothesis has less support than it might have
seemed: the most recent community data point available (Jan 2025) still describes Denuvo as present,
and a second independent tool's design (MMConsole) is consistent with that too. **Net effect: shift
the honest-uncertainty needle slightly toward "still present," not toward "confirmed removed."**
Possible reconciling explanations worth checking live, in rough order of plausibility:
1. A **different/updated Denuvo integration** that doesn't use the same exported-function-name
   pattern (`GetDenuvoTicketLocation` etc.) Burnout Paradise's older integration used, and/or stores
   its activation state somewhere other than the specific `dbdata` filename previously assumed.
2. The specific string/file checks performed didn't cover every possible signature (worth a second,
   broader static pass if this remains a live question).
3. Some genuinely unusual local factor (a very recent patch this search pass's sources predate).

## Concrete next step

No change to the existing plan — `ENGINE-DOSSIER.md` §4 already correctly defers final judgment to
the first live debugger attach. This topic exists so that decision is made with the most current
evidence available, not the first-pass search's older threads. If a debugger attach goes smoothly
with no anti-debug resistance at all, that itself would be worth treating as meaningful evidence
Denuvo really is absent from this build — genuinely surprising given the balance of evidence here,
and worth flagging back to external-research if so.

## Sources

- https://steamcommunity.com/app/234140/discussions/0/600766396226376603/
