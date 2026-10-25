"""Educational walk-in cooler/freezer box-load sizer (stdlib). NOT for stamped bids."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from ._common import prompt_float as pf

DISCLAIMER = (
    "EDUCATIONAL ONLY — not for stamped bids or equipment selection.\n"
    "Use manufacturer software and ASHRAE methods for real design work.\n"
    "All factors are approximate practice values, not certified data."
)
BOX = {"cooler": 35.0, "freezer": -10.0, "custom": None}
INSUL = {
    "cooler-4in-foam": 28.0,
    "freezer-5in-foam": 35.0,
    "freezer-6in-foam": 42.0,
    "thin-2in": 14.0,
}
FLOOR = {"insulated": None, "on-grade": 8.0, "none": 9999.0}  # insulated => match walls
USAGE = {
    "light": (20, 4.0),
    "medium": (50, 8.0),
    "heavy": (100, 14.0),
}  # openings/day, ACPD
# product: cp, latent, resp_btu_per_lb_day
PROD = {
    "packaged-meat": (0.75, 0.0, 0.0),
    "produce": (0.90, 0.0, 40.0),
    "dairy": (0.90, 0.0, 5.0),
    "frozen-food": (0.45, 144.0, 0.0),
    "beverage": (1.00, 0.0, 0.0),
    "custom": (0.80, 0.0, 0.0),
}
W2Q = 3.412


@dataclass
class In:
    L: float
    W: float
    H: float
    box: str
    target: float
    ambient: float
    wall_r: float
    ceil_r: float
    floor_r: float
    door_a: float
    opens: float
    acpd: float
    prod: str
    enter: float
    lbs: float
    cp: float
    latent: float
    resp: float
    lights_w: float
    people_h: float
    people_q: float
    fans_w: float
    defrost: str
    d_kw: float
    d_h: float
    safety: float


def areas(L, W, H):
    return 2 * (L * H + W * H), L * W, L * W, L * W * H


def q_tx(Aw, Ac, Af, Rw, Rc, Rf, dT):
    q = Aw / Rw * dT + Ac / Rc * dT
    if Rf < 5000:
        q += Af / Rf * dT
    return q


def q_inf(vol, acpd, dT, door_a, opens):
    cfm = vol * (acpd / 24.0) / 60.0
    q = cfm * 1.08 * dT
    if door_a > 0 and opens > 0:
        cfm2 = (door_a * 7.0 * opens) / (24.0 * 60.0)
        q += cfm2 * 1.08 * dT
    return q


def q_prod(lbs, enter, box_f, cp, latent, resp):
    if lbs <= 0:
        return 0.0
    sens = lbs * cp * max(enter - box_f, 0) / 24.0
    lat = lbs * latent / 24.0 if (latent > 0 and enter > 32 and box_f < 32) else 0.0
    return sens + lat + lbs * resp / 24.0


def q_misc(lights, ph, pq, fans, defrost, dkw, dh):
    q = lights * W2Q + pq * (ph / 24.0) + fans * W2Q
    if defrost == "electric" and dkw > 0 and dh > 0:
        q += dkw * 1000 * W2Q * (dh / 24.0)
    return q


def suggest(total):
    bands = [
        (3000, "≈ 2–3k BTU/hr"),
        (6000, "≈ 3–6k BTU/hr"),
        (9000, "≈ 6–9k BTU/hr"),
        (12000, "≈ 9–12k BTU/hr (~1 ton)"),
        (18000, "≈ 12–18k BTU/hr"),
        (24000, "≈ 18–24k BTU/hr"),
        (36000, "≈ 24–36k BTU/hr"),
        (48000, "≈ 36–48k BTU/hr"),
        (60000, "≈ 48–60k BTU/hr"),
        (90000, "≈ 60–90k BTU/hr"),
        (120000, "≈ 90–120k BTU/hr"),
    ]
    for lim, lab in bands:
        if total <= lim:
            return lab + " class"
    return "≈ 120k+ BTU/hr class (multi-evap / out of simple v1 scope)"


def calc(i: In):
    Aw, Ac, Af, vol = areas(i.L, i.W, i.H)
    dT = i.ambient - i.target
    if dT <= 0:
        raise ValueError("Ambient must be warmer than box target.")
    if not (10 <= i.safety <= 20):
        raise ValueError("Safety factor must be 10–20%.")
    tx = q_tx(Aw, Ac, Af, i.wall_r, i.ceil_r, i.floor_r, dT)
    inf = q_inf(vol, i.acpd, dT, i.door_a, i.opens)
    pr = q_prod(i.lbs, i.enter, i.target, i.cp, i.latent, i.resp)
    misc = q_misc(i.lights_w, i.people_h, i.people_q, i.fans_w, i.defrost, i.d_kw, i.d_h)
    sub = tx + inf + pr + misc
    tot = sub * (1 + i.safety / 100)
    return dict(
        vol=vol, dT=dT, tx=tx, inf=inf, pr=pr, misc=misc, sub=sub, tot=tot, sug=suggest(tot)
    )


def report(i: In, r: dict):
    print("\n" + "=" * 64)
    print("Walk-in box load estimate (educational)")
    print("=" * 64)
    print(DISCLAIMER)
    print(f"\nBox: {i.L:.1f}×{i.W:.1f}×{i.H:.1f} ft | Vol {r['vol']:.0f} ft³")
    print(f"Type: {i.box} @ {i.target:.1f}°F | Amb {i.ambient:.1f}°F | ΔT {r['dT']:.1f}°F")
    print(f"R — walls {i.wall_r:.1f} / ceil {i.ceil_r:.1f} / floor {i.floor_r:.1f}")
    print(f"Usage — door {i.door_a:.1f} ft², {i.opens:.0f} opens/day, ACPD {i.acpd:.1f}")
    print(f"Product — {i.prod}: {i.lbs:.0f} lb/day from {i.enter:.1f}°F\n")
    print("--- Load breakdown (BTU/hr) ---")
    print(f"  Transmission:   {r['tx']:10.0f}")
    print(f"  Infiltration:   {r['inf']:10.0f}  (incl. door approx)")
    print(f"  Product:        {r['pr']:10.0f}  (sensible/latent/resp approx)")
    print(f"  Misc:           {r['misc']:10.0f}  (lights/people/fans/defrost)")
    print(f"  Subtotal:       {r['sub']:10.0f}")
    print(f"  Safety {i.safety:.0f}%:     {r['tot'] - r['sub']:10.0f}")
    print(f"  TOTAL w/ SF:    {r['tot']:10.0f}")
    print(f"\nRough unit suggestion band: {r['sug']}")
    print("\nOut of scope v1: glass cases, blast chillers, CO₂ racks, humidity,")
    print("multi-evap balance, full psychrometric infiltration.")
    print("=" * 64)


def pc(label, choices, default):
    while True:
        s = input(f"{label} ({'/'.join(choices)}) [{default}]: ").strip().lower() or default
        if s in choices:
            return s
        print("Invalid choice.")


def interactive():
    print("Commercial walk-in box-load sizer (educational)\n" + DISCLAIMER + "\n")
    L, W, H = pf("Length ft", 10), pf("Width ft", 8), pf("Height ft", 8)
    box = pc("Box type", list(BOX), "cooler")
    target = pf("Target °F", 35) if box == "custom" else float(BOX[box])
    if box != "custom":
        print(f"Using target {target:.0f}°F")
    amb = pf("Ambient °F", 95)
    ins = pc("Insulation", list(INSUL), "cooler-4in-foam")
    wr = cr = float(INSUL[ins])
    ovr = input("Override wall/ceiling R (blank=keep): ").strip()
    if ovr:
        wr = cr = float(ovr)
    fl = pc("Floor", list(FLOOR), "insulated")
    fr = wr if fl == "insulated" else float(FLOOR[fl])
    use = pc("Usage", list(USAGE), "medium")
    opens, acpd = USAGE[use]
    door_a = pf("Door width ft", 3) * pf("Door height ft", 7)
    acpd = pf("ACPD", acpd)
    opens = pf("Openings/day", opens)
    prod = pc("Product", list(PROD), "packaged-meat")
    cp, lat, resp = PROD[prod]
    enter = pf("Entering product °F", 50 if box != "freezer" else 0)
    mode = pc("Product mode", ["lbs", "turnover"], "lbs")
    vol = L * W * H
    lbs = (
        vol * 25 * (pf("Turnover % of volume/day", 10) / 100)
        if mode == "turnover"
        else pf("lb/day", 500)
    )
    if mode == "turnover":
        print(f"Approx {lbs:.0f} lb/day")
    if prod == "custom":
        cp = pf("cp BTU/lb·°F", cp)
        lat = pf("latent BTU/lb", 0)
        resp = pf("resp BTU/lb·day", 0)
    lights = pf("Lights W", 120)
    ph = pf("People-hours/day", 2)
    pq = pf("People BTU/hr", 500)
    fans = pf("Evap fans W", 200)
    deft = pc(
        "Defrost", ["electric", "hot-gas", "none"], "electric" if box == "freezer" else "none"
    )
    dkw = dh = 0.0
    if deft == "electric":
        dkw = pf("Defrost kW", 3)
        dh = pf("Defrost h/day", 1.5)
    safety = min(20, max(10, pf("Safety % 10-20", 15)))
    i = In(
        L,
        W,
        H,
        box,
        target,
        amb,
        wr,
        cr,
        fr,
        door_a,
        opens,
        acpd,
        prod,
        enter,
        lbs,
        cp,
        lat,
        resp,
        lights,
        ph,
        pq,
        fans,
        deft,
        dkw,
        dh,
        safety,
    )
    report(i, calc(i))
    return 0


def build():
    p = argparse.ArgumentParser(
        description="Educational walk-in box-load estimator. NOT for stamped bids."
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--length", type=float)
    p.add_argument("--width", type=float)
    p.add_argument("--height", type=float)
    p.add_argument("--box-type", choices=list(BOX), default="cooler")
    p.add_argument("--target-f", type=float)
    p.add_argument("--ambient-f", type=float, default=95)
    p.add_argument("--insulation", choices=list(INSUL), default="cooler-4in-foam")
    p.add_argument("--wall-r", type=float)
    p.add_argument("--ceiling-r", type=float)
    p.add_argument("--floor", choices=list(FLOOR), default="insulated")
    p.add_argument("--floor-r", type=float)
    p.add_argument("--usage", choices=list(USAGE), default="medium")
    p.add_argument("--door-w", type=float, default=3)
    p.add_argument("--door-h", type=float, default=7)
    p.add_argument("--openings-day", type=float)
    p.add_argument("--acpd", type=float)
    p.add_argument("--product", choices=list(PROD), default="packaged-meat")
    p.add_argument("--product-enter-f", type=float, default=50)
    p.add_argument("--product-lbs-day", type=float, default=500)
    p.add_argument("--turnover-pct", type=float)
    p.add_argument("--lights-w", type=float, default=120)
    p.add_argument("--people-hours", type=float, default=2)
    p.add_argument("--people-btu-hr", type=float, default=500)
    p.add_argument("--fans-w", type=float, default=200)
    p.add_argument("--defrost", choices=["electric", "hot-gas", "none"], default="none")
    p.add_argument("--defrost-kw", type=float, default=0)
    p.add_argument("--defrost-hours-day", type=float, default=0)
    p.add_argument("--safety-pct", type=float, default=15)
    return p


def from_args(a):
    if a.box_type == "custom":
        if a.target_f is None:
            raise ValueError("--target-f required for custom")
        target = a.target_f
    else:
        target = a.target_f if a.target_f is not None else float(BOX[a.box_type])
    wr = float(INSUL[a.insulation]) if a.wall_r is None else a.wall_r
    cr = wr if a.ceiling_r is None else a.ceiling_r
    if a.floor_r is not None:
        fr = a.floor_r
    elif a.floor == "insulated":
        fr = wr
    else:
        fr = float(FLOOR[a.floor])
    opens, acpd = USAGE[a.usage]
    if a.openings_day is not None:
        opens = a.openings_day
    if a.acpd is not None:
        acpd = a.acpd
    cp, lat, resp = PROD[a.product]
    vol = a.length * a.width * a.height
    lbs = vol * 25 * (a.turnover_pct / 100) if a.turnover_pct is not None else a.product_lbs_day
    if not (10 <= a.safety_pct <= 20):
        raise ValueError("--safety-pct must be 10–20")
    return In(
        a.length,
        a.width,
        a.height,
        a.box_type,
        target,
        a.ambient_f,
        wr,
        cr,
        fr,
        a.door_w * a.door_h,
        opens,
        acpd,
        a.product,
        a.product_enter_f,
        lbs,
        cp,
        lat,
        resp,
        a.lights_w,
        a.people_hours,
        a.people_btu_hr,
        a.fans_w,
        a.defrost,
        a.defrost_kw,
        a.defrost_hours_day,
        a.safety_pct,
    )


def main(argv=None):
    p = build()
    a = p.parse_args(argv)
    if a.interactive or (
        a.length is None and a.width is None and a.height is None and len(sys.argv) == 1
    ):
        return interactive()
    miss = [n for n in ("length", "width", "height") if getattr(a, n) is None]
    if miss:
        print(f"Error: need {', '.join('--' + m for m in miss)} (or -i)", file=sys.stderr)
        return 1
    try:
        i = from_args(a)
        report(i, calc(i))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
