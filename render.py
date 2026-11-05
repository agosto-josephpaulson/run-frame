"""Render 800x480 screens for the Waveshare PhotoPainter (Spectra 6 e-paper).

Usage: python render.py data.json outdir/
Writes one PNG per screen plus current.png (the screen for this hour's slot).
"""
import json, sys, math, datetime as dt
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 800, 480
# Spectra 6 primaries (pure values; the firmware maps them to panel pigments)
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
RED, YELLOW, BLUE, GREEN = (255, 0, 0), (255, 255, 0), (0, 0, 255), (0, 255, 0)
PALETTE = [BLACK, WHITE, RED, YELLOW, BLUE, GREEN]

import os, glob
_FONTS = {}
def _font_path(weight):
    if weight not in _FONTS:
        roots = [os.environ.get("FONT_DIR", ""), "fonts", "/usr/share/fonts"]
        for root in filter(None, roots):
            hits = glob.glob(f"{root}/**/Inter-{weight}.otf", recursive=True) + \
                   glob.glob(f"{root}/**/Inter-{weight}.ttf", recursive=True)
            if hits:
                _FONTS[weight] = sorted(hits, key=len)[0]
                break
        else:
            raise FileNotFoundError(f"Inter-{weight} font not found")
    return _FONTS[weight]
def F(size, weight="Bold"):
    return ImageFont.truetype(_font_path(weight), size)

def quantize(img):
    pal = Image.new("P", (1, 1))
    flat = sum(PALETTE, ()) + (0, 0, 0) * (256 - len(PALETTE))
    pal.putpalette(flat)
    return img.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB")

def canvas():
    img = Image.new("RGB", (W, H), WHITE)
    return img, ImageDraw.Draw(img)

def header(d, title, right=""):
    d.rectangle([0, 0, W, 44], fill=BLACK)
    d.text((20, 22), title, font=F(22, "ExtraBold"), fill=WHITE, anchor="lm")
    if right:
        d.text((W - 20, 22), right, font=F(18, "SemiBold"), fill=WHITE, anchor="rm")

def footer(d, nxt):
    if not nxt:
        return
    d.rectangle([0, 448, W, H], fill=BLACK)
    d.text((20, 464), "NEXT", font=F(18, "Black"), fill=YELLOW, anchor="lm")
    d.text((84, 464), f"{nxt['when']} · {nxt['what']}", font=F(18, "Bold"), fill=WHITE, anchor="lm")

def fmt(n, dec=0):
    return f"{n:,.{dec}f}"

# ---------------------------------------------------------------- 1. Goal
def screen_goal(data):
    img, d = canvas()
    today = dt.date.fromisoformat(data["today"])
    year = today.year
    goal = data["goal_miles"]
    daily = data["daily"]
    jan1 = dt.date(year, 1, 1)
    days_in_year = (dt.date(year + 1, 1, 1) - jan1).days
    doy = (today - jan1).days + 1
    ytd = sum(v.get("run_mi", 0) for k, v in daily.items() if k.startswith(str(year)))
    pace_target = goal * doy / days_in_year
    delta = ytd - pace_target
    remaining = max(goal - ytd, 0)
    days_left = days_in_year - doy
    need_wk = remaining / max(days_left, 1) * 7

    header(d, f"{year} · {fmt(goal)} MILES", today.strftime("%a %b %-d"))

    # Big number
    size = 150
    while d.textlength(fmt(ytd), font=F(size, "Black")) > 360:
        size -= 6
    d.text((30, 70 + (150 - size) // 2), fmt(ytd), font=F(size, "Black"), fill=BLACK, anchor="lt")
    d.text((36, 236), f"of {fmt(goal)} miles", font=F(30, "SemiBold"), fill=BLACK, anchor="lt")

    color = GREEN if delta >= 0 else RED
    label = f"{fmt(abs(delta))} mi {'AHEAD' if delta >= 0 else 'BEHIND'}"
    bx = d.textbbox((36, 290), label, font=F(34, "ExtraBold"))
    d.rectangle([bx[0] - 10, bx[1] - 8, bx[2] + 10, bx[3] + 8], fill=color)
    d.text((36, 290), label, font=F(34, "ExtraBold"), fill=BLACK if color == GREEN else WHITE)

    if remaining == 0:
        d.text((36, 340), "GOAL HIT.", font=F(24, "ExtraBold"), fill=BLACK)
        d.text((36, 370), "Accruing bonus miles.", font=F(20, "Regular"), fill=BLACK)
    else:
      d.text((36, 340), f"Need {need_wk:.1f} mi/week to finish", font=F(24, "SemiBold"), fill=BLACK)
      d.text((36, 370), f"{days_left} days left · {remaining:.0f} mi to go", font=F(20, "Regular"), fill=BLACK)

    # Cumulative chart (right)
    cx0, cy0, cx1, cy1 = 420, 76, 770, 392
    d.line([cx0, cy1, cx1, cy1], fill=BLACK, width=2)
    d.line([cx0, cy0, cx0, cy1], fill=BLACK, width=2)
    top = max(goal * 1.1, ytd * 1.08)
    def px(day_idx, miles):
        x = cx0 + (cx1 - cx0) * day_idx / days_in_year
        y = cy1 - (cy1 - cy0) * min(miles, top) / top
        return x, y
    # pace line (dashed)
    for i in range(0, days_in_year, 8):
        d.line([px(i, goal * i / days_in_year), px(i + 4, goal * (i + 4) / days_in_year)], fill=BLUE, width=3)
    gy = px(0, goal)[1]
    d.text((cx0 + 6, gy - 4), fmt(goal), font=F(16, "Bold"), fill=BLUE, anchor="lb")
    # actual
    pts, cum = [], 0
    for i in range(doy):
        k = (jan1 + dt.timedelta(days=i)).isoformat()
        cum += daily.get(k, {}).get("run_mi", 0)
        pts.append(px(i, cum))
    d.line(pts, fill=RED, width=5)
    d.ellipse([pts[-1][0] - 7, pts[-1][1] - 7, pts[-1][0] + 7, pts[-1][1] + 7], fill=RED)

    # progress bar bottom
    d.rectangle([30, 410, 770, 432], outline=BLACK, width=2)
    tx = 32 + 736 * min(pace_target / goal, 1)
    d.rectangle([32, 412, tx, 430], fill=BLUE)
    d.line([tx, 404, tx, 438], fill=BLACK, width=3)
    return img

# ---------------------------------------------------------------- 2. Streak calendar
CAL_LAYOUT = "blocks"   # "blocks" = 10-high month blocks, "weeks" = weekday rows with month gaps

def _cal_positions(year, layout):
    """Yield (date, x, y, dia) for every day of the year, plus month label positions."""
    pos, labels = {}, []
    if layout == "blocks":
        rows, pitch, dia, mgap = 11, 15, 10, 14
        gx, gy = 30, 100
        x = gx
        for m in range(1, 13):
            first = dt.date(year, m, 1)
            ndays = ((dt.date(year + (m == 12), m % 12 + 1, 1)) - first).days
            labels.append((x, first.strftime("%b")))
            for i in range(ndays):
                pos[first + dt.timedelta(days=i)] = (x + (i // rows) * pitch, gy + (i % rows) * pitch)
            x += math.ceil(ndays / rows) * pitch + mgap
        return pos, labels, dia, gy + rows * pitch, None
    else:
        pitch, dia, mgap = 11, 8, 7
        gx, gy = 30, 100
        x = gx
        for m in range(1, 13):
            first = dt.date(year, m, 1)
            ndays = ((dt.date(year + (m == 12), m % 12 + 1, 1)) - first).days
            labels.append((x, first.strftime("%b")))
            ncols = 0
            for i in range(ndays):
                day = first + dt.timedelta(days=i)
                col = (i + first.weekday()) // 7
                ncols = max(ncols, col + 1)
                pos[day] = (x + col * pitch, gy + day.weekday() * pitch)
            x += ncols * pitch + mgap
        return pos, labels, dia, gy + 7 * pitch, None

def screen_calendar(data, layout=None):
    layout = layout or data.get("cal_layout", CAL_LAYOUT)
    img, d = canvas()
    today = dt.date.fromisoformat(data["today"])
    year = today.year
    daily = data["daily"]
    BOTH = RED
    header(d, f"{year} · EVERY DAY COUNTS", today.strftime("%a %b %-d"))

    pos, labels, dia, bottom, _ = _cal_positions(year, layout)
    for x, lab in labels:
        d.text((x, 76), lab, font=F(14, "SemiBold"), fill=BLACK)

    run_days = lift_days = active = streak = best = 0
    for day in sorted(pos):
        x, y = pos[day]
        box = [x, y, x + dia, y + dia]
        v = daily.get(day.isoformat(), {})
        ran, lifted = v.get("run_mi", 0) > 0, v.get("lift", False)
        if day > today or (day == today and not (ran or lifted)):
            d.ellipse(box, outline=BLACK, width=1)   # future / today so far: empty ring
            if day == today:
                d.rectangle([x - 3, y - 3, x + dia + 3, y + dia + 3], outline=BLACK, width=2)
            continue
        if ran and lifted: d.ellipse(box, fill=BOTH)
        elif ran: d.ellipse(box, fill=GREEN)
        elif lifted: d.ellipse(box, fill=BLUE)
        else: d.ellipse(box, fill=BLACK)   # past, nothing logged
        run_days += ran; lift_days += lifted
        if ran or lifted:
            active += 1; streak += 1; best = max(best, streak)
        else:
            streak = 0
        if day == today:
            d.rectangle([x - 3, y - 3, x + dia + 3, y + dia + 3], outline=BLACK, width=2)

    ly = bottom + 14
    for i, (k, lab) in enumerate([(GREEN, "Run"), (BLUE, "Lift"), (BOTH, "Run + lift"), (BLACK, "Missed / off"), (None, "Ahead")]):
        x = 30 + i * 150
        b = [x + 2, ly + 2, x + 14, ly + 14]
        if k: d.ellipse(b, fill=k)
        else: d.ellipse(b, outline=BLACK, width=1)
        d.text((x + 24, ly + 8), lab, font=F(16, "SemiBold"), fill=BLACK, anchor="lm")

    ty = ly + 40
    d.line([30, ty, W - 30, ty], fill=BLACK, width=2)
    stats = [(str(active), "active days"), (str(run_days), "run days"), (str(lift_days), "lift days"), (str(best), "best streak (days)")]
    sw = (W - 60) / 4
    big = 84 if layout == "weeks" else 72
    for i, (n, lab) in enumerate(stats):
        x = 30 + i * sw
        d.text((x, ty + 18), n, font=F(big, "Black"), fill=BLACK)
        d.text((x + 2, ty + 28 + big), lab, font=F(18, "SemiBold"), fill=BLACK)
    return img

# ---------------------------------------------------------------- 3. Latest workout
def screen_latest(data):
    img, d = canvas()
    a = data["latest"]
    if not a:
        header(d, "LATEST RUN")
        d.text((400, 260), "No runs yet", font=F(40, "Black"), fill=BLACK, anchor="mm")
        return img
    when = dt.datetime.fromisoformat(a["start"])
    header(d, "LATEST RUN", when.strftime("%a %b %-d · %-I:%M %p"))

    # route box
    bx0, by0, bx1, by1 = 24, 60, 384, 436
    d.rectangle([bx0, by0, bx1, by1], outline=BLACK, width=2)
    pts = a.get("latlng") or []
    if len(pts) > 1:
        lats = [p[0] for p in pts]; lons = [p[1] for p in pts]
        midlat = math.radians(sum(lats) / len(lats))
        xs = [lo * math.cos(midlat) for lo in lons]
        spanx, spany = (max(xs) - min(xs)) or 1e-6, (max(lats) - min(lats)) or 1e-6
        s = min((bx1 - bx0 - 48) / spanx, (by1 - by0 - 48) / spany)
        ox = bx0 + (bx1 - bx0 - spanx * s) / 2
        oy = by0 + (by1 - by0 - spany * s) / 2
        path = [(ox + (x - min(xs)) * s, oy + (max(lats) - la) * s) for x, la in zip(xs, lats)]
        d.line(path, fill=RED, width=6, joint="curve")
        sx, sy = path[0]
        d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=GREEN, outline=BLACK, width=2)
    else:
        d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "Treadmill / no GPS", font=F(22, "SemiBold"), fill=BLACK, anchor="mm")

    x = 412
    d.text((x, 66), a["name"], font=F(26, "Bold"), fill=BLACK)
    d.text((x - 4, 100), f"{a['miles']:.2f}", font=F(110, "Black"), fill=BLACK)
    d.text((x, 222), "miles", font=F(26, "SemiBold"), fill=BLACK)
    secs = a["moving_s"]
    pace = secs / a["miles"]
    rows = [("TIME", f"{secs // 3600}:{secs % 3600 // 60:02d}:{secs % 60:02d}" if secs >= 3600 else f"{secs // 60}:{secs % 60:02d}"),
            ("PACE", f"{int(pace // 60)}:{int(pace % 60):02d} /mi"),
            ("AVG HR", f"{a['avg_hr']} bpm"),
            ("CLIMB", f"{fmt(a['elev_ft'])} ft")]
    for i, (k, v) in enumerate(rows):
        cx = x + (i % 2) * 190
        cy = 280 + (i // 2) * 88
        d.text((cx, cy), k, font=F(16, "Bold"), fill=BLUE)
        d.text((cx, cy + 22), v, font=F(34, "ExtraBold"), fill=BLACK)
    return img

# ---------------------------------------------------------------- 5. Race countdown
def screen_countdown(data):
    img, d = canvas()
    today = dt.date.fromisoformat(data["today"])
    r = data["race"]
    rd = dt.date.fromisoformat(r["date"])
    days = (rd - today).days
    header(d, r["name"].upper(), rd.strftime("%a %b %-d, %Y"))

    d.text((30, 64), str(days), font=F(170, "Black"), fill=BLACK)
    d.text((36, 254), "days to go", font=F(34, "Bold"), fill=BLACK)
    d.text((36, 300), f"{days // 7} weeks, {days % 7} day{'s' if days % 7 != 1 else ''}", font=F(22, "Regular"), fill=BLACK)

    # long-run bars (minutes) for recent weeks
    lr = r["long_runs"]  # list of {"week": "Oct 20", "min": 75}
    target = r.get("long_run_goal_min", 120)
    cx0, cy0, cx1, cy1 = 400, 104, 776, 372
    d.text((cx0, 64), "LONGEST RUN EACH WEEK", font=F(16, "Bold"), fill=BLUE)
    top = target * 1.6
    bw = (cx1 - cx0) / len(lr)
    for i, w in enumerate(lr):
        h = (cy1 - cy0) * min(w["min"], top) / top
        x0 = cx0 + i * bw + 5
        d.rectangle([x0, cy1 - h, x0 + bw - 10, cy1], fill=GREEN if w["min"] >= target else BLACK)
        d.text((x0 + (bw - 10) / 2, cy1 - h - 4), str(w["min"]), font=F(14, "Bold"), fill=BLACK, anchor="mb")
        d.text((x0 + (bw - 10) / 2, cy1 + 8), w["week"], font=F(12, "SemiBold"), fill=BLACK, anchor="mt")
    ty = cy1 - (cy1 - cy0) * target / top
    for xx in range(cx0, cx1, 14):
        d.line([xx, ty, xx + 7, ty], fill=RED, width=3)
    d.text((cx1, ty - 6), f"goal {target} min", font=F(14, "Bold"), fill=RED, anchor="rb")

    d.rectangle([30, 404, 770, 434], fill=YELLOW)
    d.text((400, 419), r.get("tagline", "Goal: time on feet"), font=F(18, "Bold"), fill=BLACK, anchor="mm")
    return img

# ---------------------------------------------------------------- 7. Inspiration
CITIES = [  # approx driving miles from Minneapolis
    (410, "Chicago"), (915, "Denver"), (1200, "New York City"), (1650, "Seattle"),
    (1930, "Los Angeles"), (3100, "Anchorage"), (24900, "around the Earth")]

def screen_inspo(data):
    img, d = canvas()
    today = dt.date.fromisoformat(data["today"])
    i = data["inspo"]
    header(d, "KEEP GOING", today.strftime("%a %b %-d"))

    ly = i.get("last_year")
    d.text((30, 66), "ONE YEAR AGO TODAY", font=F(16, "Bold"), fill=BLUE)
    if ly:
        d.text((30, 90), f"{ly['miles']:.1f} mi", font=F(64, "Black"), fill=BLACK)
        d.text((30, 166), ly["name"], font=F(22, "SemiBold"), fill=BLACK)
    else:
        d.text((30, 90), "Rest day.", font=F(64, "Black"), fill=BLACK)
        d.text((30, 166), "Today doesn't have to be.", font=F(22, "SemiBold"), fill=BLACK)

    life = i["lifetime_miles"]
    passed = [c for c in CITIES if c[0] <= life]
    nxt = next((c for c in CITIES if c[0] > life), None)
    d.text((420, 66), "LIFETIME ON FEET", font=F(16, "Bold"), fill=BLUE)
    d.text((420, 90), f"{fmt(life)} mi", font=F(64, "Black"), fill=BLACK)
    if passed:
        d.text((420, 166), f"Farther than home → {passed[-1][1]}", font=F(22, "SemiBold"), fill=BLACK)
    if nxt:
        d.text((420, 196), f"{nxt[0] - life:,.0f} mi to {nxt[1]}", font=F(22, "Regular"), fill=BLACK)

    d.line([30, 240, 770, 240], fill=BLACK, width=2)
    d.text((30, 256), "BEST OF THIS YEAR", font=F(16, "Bold"), fill=BLUE)
    for k, (lab, val) in enumerate(i["bests"][:3]):
        x = 30 + k * 250
        d.text((x, 276), val, font=F(40, "Black"), fill=BLACK)
        d.text((x, 324), lab, font=F(18, "SemiBold"), fill=BLACK)

    d.rectangle([0, 356, W, 448], fill=RED)
    for k, ln in enumerate(i.get("mantra") or ["Run regularly", "Not too fast", "Mostly trails"]):
        d.text((400, 375 + k * 27), ln, font=F(26, "ExtraBold"), fill=WHITE, anchor="mm")
    return img

SCREENS = [("goal", screen_goal), ("calendar", screen_calendar), ("latest", screen_latest),
           ("countdown", screen_countdown), ("inspo", screen_inspo)]

def main(data_path, out):
    data = json.loads(Path(data_path).read_text())
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    imgs = {}
    for name, fn in SCREENS:
        img = fn(data)
        footer(ImageDraw.Draw(img), data.get("next"))
        img = quantize(img)
        img.save(out / f"{name}.png")
        imgs[name] = img
    hour = dt.datetime.fromisoformat(data.get("now", data["today"] + "T12:00")).hour
    slot = SCREENS[hour % len(SCREENS)][0]
    imgs[slot].save(out / "current.png")
    imgs[slot].save(out / "current.jpg", quality=95, subsampling=0)
    (out / "index.html").write_text("<!doctype html><title>run-frame</title><body style='background:#ccc'>"
        + f"<p>Updated {data.get('now','')} · showing <b>{slot}</b></p>"
        + "".join(f"<p><img src='{n}.png' width=800></p>" for n, _ in SCREENS) + "</body>")
    print("current ->", slot)

if __name__ == "__main__":
    main(*sys.argv[1:3])
