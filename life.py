"""Life-clock mockups: life % screen and month-grid life calendar (800x480, Spectra 6)."""
import datetime as dt
from render import *  # canvas, F, quantize, colors, W, H

# SSA 2023 period life table (2026 Trustees Report), male q(x), ages 0-119
Q = [float(x) for x in """0.006015,0.000479,0.000320,0.000249,0.000194,0.000159,0.000137,0.000125,0.000120,0.000120,0.000125,0.000140,0.000173,0.000233,0.000327,0.000463,0.000634,0.000819,0.000999,0.001138,0.001235,0.001315,0.001378,0.001439,0.001509,0.001595,0.001685,0.001783,0.001876,0.001970,0.002085,0.002202,0.002308,0.002407,0.002490,0.002577,0.002665,0.002764,0.002864,0.002987,0.003115,0.003253,0.003419,0.003600,0.003777,0.003931,0.004073,0.004245,0.004477,0.004795,0.005126,0.005496,0.005917,0.006404,0.006923,0.007491,0.008173,0.008938,0.009714,0.010494,0.011337,0.012232,0.013196,0.014229,0.015316,0.016455,0.017574,0.018735,0.019981,0.021366,0.022903,0.024615,0.026504,0.028648,0.031071,0.033802,0.037010,0.041158,0.045461,0.050346,0.055633,0.061757,0.068358,0.075420,0.083364,0.092680,0.103459,0.115502,0.129018,0.143810,0.159458,0.176551,0.195360,0.216286,0.238799,0.262268,0.286291,0.310944,0.332325,0.349036,0.366568,0.38496,0.404252,0.424488,0.445712,0.467998,0.491398,0.515968,0.541766,0.568854,0.597297,0.627162,0.65852,0.691446,0.726018,0.762319,0.800435,0.840457,0.88248,0.926604""".split(",")]
assert len(Q) == 120

BIRTH = dt.date(1989, 2, 12)
BIRTHS = {(b.year - 1989) * 12 + (b.month - 2) for b in (dt.date(2024, 12, 12), dt.date(2026, 7, 10))}
TODAY = dt.date.today()   # render.py overrides with the data date
FIT_HR = 0.75   # mortality multiplier for VO2max 49 (~77th pct, men 30-39)

def model(today=None, hr=FIT_HR):
    today = today or TODAY
    age = (today - BIRTH).days / 365.2425
    a0 = int(age)
    frac = age - a0
    # survival curve by month from today, monthly hazard from annual q
    surv, s = [], 1.0
    months_left = 0.0
    a = age
    while s > 1e-5 and a < 119.9:
        q = min(1.0, Q[int(a)] * hr)
        mq = 1 - (1 - q) ** (1 / 12)
        months_left += s * (1 - mq / 2)
        s *= 1 - mq
        a += 1 / 12
        surv.append((a, s))
    exp_age = age + months_left / 12
    def p_reach(x):
        for aa, ss in surv:
            if aa >= x:
                return ss
        return 0.0
    # median
    med = next(aa for aa, ss in surv if ss <= 0.5)
    return dict(age=age, exp_age=exp_age, months_left=months_left, median=med,
                p80=p_reach(80), p90=p_reach(90), p100=p_reach(100))

def screen_lifepct(m):
    img, d = canvas()
    pct = m["age"] / m["exp_age"] * 100
    d.rectangle([0, 0, W, 44], fill=BLACK)
    d.text((20, 22), "LIFE CLOCK", font=F(22, "ExtraBold"), fill=WHITE, anchor="lm")
    d.text((W - 20, 22), f"Age {m['age']:.1f} · Projected {m['exp_age']:.1f}", font=F(18, "SemiBold"), fill=WHITE, anchor="rm")
    # big number
    d.text((24, 64), f"{pct:.1f}%", font=F(150, "Black"), fill=BLACK)
    d.text((34, 256), "of your projected life lived so far", font=F(26, "Bold"), fill=BLACK)
    # right column stats
    left_mo = m["months_left"]
    stats = [
        (f"{left_mo/12:.1f}", "years ahead"),
        (f"{left_mo:,.0f}", "months ahead"),
        (f"{int(left_mo/12)}", "summers ahead"),
    ]
    y = 74
    for big, small in stats:
        d.text((566, y), big, font=F(36, "ExtraBold"), fill=BLUE, anchor="la")
        d.text((566, y + 40), small, font=F(16, "SemiBold"), fill=BLACK, anchor="la")
        y += 82
    d.line([546, 62, 546, 318], fill=BLACK, width=2)
    # bar
    x0, x1, by0, by1 = 30, 770, 336, 372
    d.rectangle([x0, by0, x1, by1], outline=BLACK, width=3)
    fx = x0 + (x1 - x0) * pct / 100
    d.rectangle([x0, by0, fx, by1], fill=BLUE)
    # decade ticks
    for dec in range(10, int(m["exp_age"]) - 3, 10):
        tx = x0 + (x1 - x0) * dec / m["exp_age"]
        d.line([tx, by1, tx, by1 + 8], fill=BLACK, width=2)
        d.text((tx, by1 + 10), str(dec), font=F(15, "SemiBold"), fill=BLACK, anchor="ma")
    d.text((x1, by1 + 10), f"{m['exp_age']:.0f}", font=F(15, "Bold"), fill=BLACK, anchor="ra")
    # mantra band
    d.rectangle([0, 410, W, H], fill=YELLOW)
    d.text((W // 2, 445), "Live today like you came back for it.", font=F(26, "ExtraBold"), fill=BLACK, anchor="mm")
    return img

def screen_lifecal(m):
    img, d = canvas()
    d.rectangle([0, 0, W, 44], fill=BLACK)
    d.text((20, 22), "LIFE IN MONTHS", font=F(22, "ExtraBold"), fill=WHITE, anchor="lm")
    lived = int(m["age"] * 12)
    exp_mo = int(round(m["exp_age"] * 12))
    cap = int(-(-m['exp_age'] // 5) * 5)   # 81.5 -> 85
    d.text((W - 20, 22), f"{lived:,} lived · {exp_mo - lived:,} ahead", font=F(18, "SemiBold"), fill=WHITE, anchor="rm")
    # 10 decade rows x 10 years; each year = 4 cols x 3 rows of month dots
    pitch, dia = 9, 7
    yw, yh = 4 * pitch, 3 * pitch
    gx, gy = 8, 9
    ox, oy = 52, 58
    for yr in range(cap):
        dec, col = divmod(yr, 10)
        bx = ox + col * (yw + gx)
        by = oy + dec * (yh + gy)
        for mo in range(12):
            r, c = divmod(mo, 4)
            x, y = bx + c * pitch, by + r * pitch
            i = yr * 12 + mo
            box = [x, y, x + dia, y + dia]
            big = [x - 1, y - 1, x + dia + 1, y + dia + 1]
            if i in BIRTHS:
                d.ellipse(big, fill=YELLOW, outline=BLACK)
            elif i < lived:
                d.ellipse(box, fill=GREEN)
            elif i == lived:
                d.ellipse(big, fill=RED)
            elif i < exp_mo:
                d.ellipse(box, outline=BLACK)
            else:
                d.ellipse(box, outline=BLUE)
        if col == 0:
            d.text((ox - 10, by + yh / 2 - 2), str(dec * 10), font=F(14, "Bold"), fill=BLACK, anchor="rm")
    # milestone markers on the right
    rx = ox + 10 * (yw + gx) + 22
    d.text((rx, 64), "Legend", font=F(18, "ExtraBold"), fill=BLACK)
    items = [(GREEN, "fill", "Lived"), (RED, "fill", "This month"),
             (YELLOW, "fill", "Clark & Ethan born"),
             (BLACK, "ring", "Ahead"), (BLUE, "ring", "Bonus")]
    y = 94
    for col, kind, label in items:
        if kind == "fill":
            d.ellipse([rx, y, rx + 12, y + 12], fill=col, outline=BLACK if col == YELLOW else None)
        else:
            d.ellipse([rx, y, rx + 12, y + 12], outline=col, width=2)
        d.text((rx + 22, y + 6), label, font=F(16, "SemiBold"), fill=BLACK, anchor="lm")
        y += 28
    y += 14
    for big, small in [(f"{m['age']/m['exp_age']*100:.0f}%", "lived"),
                       (f"{m['exp_age']:.1f}", "projected age")]:
        d.text((rx, y), big, font=F(32, "ExtraBold"), fill=BLUE)
        d.text((rx, y + 38), small, font=F(15, "SemiBold"), fill=BLACK)
        y += 66
    d.text((W // 2, 460), "SSA 2023 male table · fitness-adjusted for VO2 max 49",
           font=F(14, "Medium"), fill=BLACK, anchor="mm")
    return img

# ---------------------------------------------------------------- kids
KIDS = [("CLARK", dt.date(2024, 12, 12)), ("ETHAN", dt.date(2026, 7, 10))]
# rough hours/day together by age band (estimate): toddler, school-age, teen
def _hours(age):
    return 10 if age < 5 else 5 if age < 13 else 3

def kid_stats(born, today=None):
    today = today or TODAY
    k_year = born.year + 5 + (1 if (born.month, born.day) > (9, 1) else 0)   # MN Sept 1 cutoff
    leave = dt.date(k_year + 13, 8, 15)
    def weighted(a, b):  # integrate hours over ages a..b (years), monthly steps
        t, x = 0.0, a
        while x < b:
            t += _hours(x) / 12
            x += 1 / 12
        return t
    age_now = (today - born).days / 365.2425
    age_leave = (leave - born).days / 365.2425
    used = weighted(0, age_now) / weighted(0, age_leave)
    first_summer = born.year if born.month <= 8 else born.year + 1
    summers = list(range(first_summer, leave.year + 1))
    left = [y for y in summers if dt.date(y, 8, 31) > today]
    tot = weighted(0, age_leave)
    marks = [(a, weighted(0, a) / tot) for a in (5, 13)] + [(int(age_leave), 1.0)]
    return dict(leave=leave, used=used, summers=summers, left=len(left), marks=marks,
                age_now=age_now, age_leave=age_leave,
                weeks_left=len(left) * 13, you_at=(leave - BIRTH).days / 365.2425)

def screen_kids():
    img, d = canvas()
    d.rectangle([0, 0, W, 44], fill=BLACK)
    d.text((20, 22), "SUMMERS WITH THE BOYS", font=F(22, "ExtraBold"), fill=WHITE, anchor="lm")
    d.text((W - 20, 22), "13 summer weeks a year", font=F(18, "SemiBold"), fill=WHITE, anchor="rm")
    for i, (label, born) in enumerate(KIDS):
        k = kid_stats(born)
        y0 = 54 + i * 210
        if i:
            d.line([20, y0 - 6, W - 20, y0 - 6], fill=BLACK, width=2)
        had = len(k["summers"]) - k["left"]
        d.text((24, y0), f"{label} · age {int(k['age_now'])} · {had} summer{'s' if had != 1 else ''} together so far",
               font=F(17, "Bold"), fill=BLACK)
        d.text((22, y0 + 18), str(k["left"]), font=F(96, "Black"), fill=BLACK)
        nx = 26 + d.textlength(str(k["left"]), font=F(96, "Black")) + 10
        d.text((nx, y0 + 40), "summers ahead", font=F(26, "ExtraBold"), fill=BLACK)
        d.text((nx, y0 + 76), f"{k['weeks_left']} summer weeks till 18",
               font=F(16, "SemiBold"), fill=BLACK)
        vac = int(2 * ((k['leave'] - TODAY).days / 365.2425))
        vx = 420
        d.text((vx, y0 + 18), str(vac), font=F(72, "Black"), fill=BLUE, anchor="ma")
        d.text((vx, y0 + 100), "vacations ahead", font=F(18, "ExtraBold"), fill=BLACK, anchor="ma")
        # time-used bar
        bx0, bx1, by = 26, 520, y0 + 148
        d.text((bx0, by - 4), f"{k['used']*100:.0f}% of memories created",
               font=F(17, "Bold"), fill=BLACK, anchor="lb")
        d.rectangle([bx0, by + 2, bx1, by + 26], outline=BLACK, width=2)
        d.rectangle([bx0, by + 2, bx0 + (bx1 - bx0) * k["used"], by + 26], fill=BLUE)
        for a, frac in k["marks"]:
            tx = bx0 + (bx1 - bx0) * frac
            d.line([tx, by + 26, tx, by + 32], fill=BLACK, width=2)
            d.text((tx, by + 33), f"age {a}", font=F(13, "SemiBold"), fill=BLACK, anchor="ra" if frac == 1.0 else "ma")
        # summer-week grid: one column per summer, 13 week dots
        gx0, gy0, pitch, dia = 572, y0 + 8, 11, 8
        for c, yr in enumerate(k["summers"]):
            for w in range(13):
                x, y = gx0 + c * pitch, gy0 + w * pitch
                # week w of that summer = Jun 1 + 7w
                wk = dt.date(yr, 6, 1) + dt.timedelta(days=7 * w)
                box = [x, y, x + dia, y + dia]
                if wk + dt.timedelta(days=6) < born:
                    continue
                if wk < TODAY:
                    d.ellipse(box, fill=GREEN)
                else:
                    d.ellipse(box, outline=BLACK)
            age_then = c  # summer index == age that summer
            if age_then % 5 == 0 or c == len(k["summers"]) - 1:
                d.text((x + dia / 2, gy0 + 13 * pitch + 4), str(age_then),
                       font=F(12, "SemiBold"), fill=BLACK, anchor="ma")
    return img

def render_all():
    m = model()
    return {"lifepct": quantize(screen_lifepct(m)), "kids": quantize(screen_kids()),
            "lifecal": quantize(screen_lifecal(m))}

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    base = model(hr=1.0)
    m = model()
    print("base", {k: round(v, 3) for k, v in base.items()})
    print("fit ", {k: round(v, 3) for k, v in m.items()})
    for name, fn in [("lifepct", screen_lifepct), ("lifecal", screen_lifecal)]:
        quantize(fn(m)).save(f"{out}/{name}.png")
    for _, b in KIDS: print(kid_stats(b))
    quantize(screen_kids()).save(f"{out}/kids.png")

