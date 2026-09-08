# 2026-09-08c — `V` is a shipped first-person cockpit camera, and the last `[FLAT]` row is closed

`/lm`, dev PC. **The user unblocked this one**: the row had been stuck since 2026-09-04b because
the only save sat at *Collect the jag tip*, where the garage car is a non-enterable prop, and
this machine had only autosave slots 1 and 2 — both in the intro, checked and confirmed this
session. The user played through to **Outer Graves / *Righteous Work*** (autosave slot 3,
1:36 played), got into a car, and handed back. Everything below is mine.

Evidence: `dev-archive/recon/2026-09-08c-V-is-a-shipped-first-person-cockpit-camera/`.

---

## 1. ⭐⭐ `V` toggles a real first-person cockpit view — the row's own success criterion, met

`[verified-live 2026-09-08, n=1 toggle cycle, with two no-input controls]`

The board's reading was: *"Slot 9 / main-pass row 3 jumping from the chase position to the driver
seat ⇒ a shipped VR-shaped camera exists; nothing ⇒ record V as disproved."*

**It jumps.** Slot 9 is the frame-constant main camera, read from the proxy's matrix dump:

| step | slot 9 (x, y, z) | movement vs previous |
| --- | --- | --- |
| base (chase) | −3295.52, 345.15, 6694.77 | — |
| **no-input control** | −3295.52, 345.15, 6694.77 | **0.00 units** |
| **`V` (1st press)** | −3301.02, 342.94, 6691.52 | **6.76 units** |
| **`V` (2nd press)** | −3295.78, 344.01, 6694.69 | **6.22 units, back** |
| no-input control 2 | −3295.83, 344.00, 6694.66 | 0.06 units |

The controls are **0.00 and 0.06 units** and the two `V` presses are **6.76 and 6.22** — about a
car length, in opposite directions. This is not a marginal effect fished out of noise; the control
is essentially exact.

**And the picture agrees, which is what settles it.** `after-V-FIRST-PERSON-COCKPIT.png` is an
interior view through the windscreen with the steering wheel and dashboard in frame;
`after-V-again-back-to-chase.png` is the ordinary third-person chase camera. A clean two-way
toggle.

**Why this matters for the North Star.** This project's whole problem is decoupling the camera and
controlling its projection, and §7b established this morning that we **cannot** move the shared
matrix. `V` is a **shipped, engine-native, keyboard-reachable first-person vehicle camera** that
needs no code at all — for a driving game aimed at VR, that is the single most valuable control
surface found here.

---

## 2. The wide FOV is a GLOBAL persistent state, not a capture-mode artefact

`[measured 2026-09-08]`

hfov read **161.08°** at every point in this session:

- vehicle, chase camera
- vehicle, first-person cockpit
- **on foot**, after stepping out of the car

Against the **80.48° default** measured on 2026-09-04b. So the persistent state from §9c is not
confined to capture mode or to a camera type — it follows the player across on-foot, vehicle-chase
and vehicle-first-person views, and it survived a **~1.5 hour play session** including a region
change and mission progress.

⚠️ **An unexplained drift, recorded rather than smoothed over.** Earlier today the same measurement
read **157.38°**; it now reads **161.08°**. The user played the game in between, so I cannot
attribute the change and am not going to invent a reason. Both values are far above the 80.48°
default and the qualitative claim is unaffected, but *"the FOV set in Video Mode is exactly what you
get later"* is **not** supported — something moved it.

⚠️ Also still untested: whether the state survives a **relaunch**. It has now survived a long
session and a region change, which is more than was known, but the process has not restarted.

---

## 3. The save situation, settled

The row had said *"needs a save past the first driving mission — play there, or load a later save
if one exists on either machine"*. Checked directly this session: **only autosave slots 1 and 2
existed, both in the intro** (3–10 greyed out). There was no shortcut on this machine, which is why
the row had stayed blocked rather than simply being overlooked.

There is now **autosave slot 3** — Outer Graves, *Righteous Work*, 1:36 played — so any future
vehicle work on the dev PC can start from there rather than replaying the opening.

---

## 4. Method note: `keymap_group_*` is not a key code

`settings.ini` holds `keymap_group_enter_vehicle=17`, `keymap_group_exit_vehicle=17`,
`keymap_group_vehicle_fp_cam=21`. Those are **group ids, not key codes** — enter and exit share
`17`, which no key binding could. The 2026-09-04 `[inferred-static]` note that they "map
vehicle_fp_cam to V and enter_vehicle to R" should not be read as coming from these lines.

Empirically, on this build: **`V` toggles the cockpit camera** `[verified-live 2026-09-08]` and
**`R` exits the vehicle** `[verified-live 2026-09-08, n=1]`.

---

## 5. What is NOT established

- Whether the cockpit camera's **projection** can be driven per-eye — that is §7b's problem and is
  unchanged by this. `V` gives a good *viewpoint*, not a stereo one.
- Whether the wide FOV survives a **relaunch**.
- What moved hfov from 157.38° to 161.08°.
- Whether the cockpit view has its own FOV control separate from the global one.
- Anything about driving: the car was stationary throughout, so nothing here says how the cockpit
  camera behaves under motion, collision, or the game's speed-based FOV effects.
