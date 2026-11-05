"""Pull activities from intervals.icu and write data.json for render.py.

Env: INTERVALS_API_KEY (secret), INTERVALS_ATHLETE_ID (e.g. i786211)
"""
import json, os, sys, datetime as dt
from zoneinfo import ZoneInfo
import requests

CFG = json.load(open(os.path.join(os.path.dirname(__file__), "config.json")))
KEY = os.environ["INTERVALS_API_KEY"]
ATH = os.environ.get("INTERVALS_ATHLETE_ID", CFG["athlete_id"])
API = "https://intervals.icu/api/v1"
AUTH = ("API_KEY", KEY)
RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}
LIFT_TYPES = {"WeightTraining"}
MI = 1609.344

now = dt.datetime.now(ZoneInfo(CFG["timezone"]))
today = now.date()

def get(path, **params):
    r = requests.get(f"{API}{path}", params=params, auth=AUTH, timeout=60)
    r.raise_for_status()
    return r.json()

acts = get(f"/athlete/{ATH}/activities",
           oldest=(today - dt.timedelta(days=400)).isoformat(), newest=today.isoformat())
acts.sort(key=lambda a: a["start_date_local"])

daily = {}
runs = []
for a in acts:
    day = a["start_date_local"][:10]
    v = daily.setdefault(day, {})
    if a.get("type") in RUN_TYPES and (a.get("distance") or 0) > 0:
        v["run_mi"] = round(v.get("run_mi", 0) + a["distance"] / MI, 2)
        runs.append(a)
    elif a.get("type") in LIFT_TYPES:
        v["lift"] = True
daily = {k: v for k, v in daily.items() if v}

# ---- latest run (+ route)
latest = None
if runs:
    a = runs[-1]
    latlng = []
    try:
        streams = get(f"/activity/{a['id']}/streams.json", types="latlng")
        for s in streams:
            if s.get("type") == "latlng":
                lats, lngs = s.get("data") or [], s.get("data2") or []
                step = max(1, len(lats) // 600)
                latlng = [[la, lo] for la, lo in zip(lats[::step], lngs[::step]) if la and lo]
    except Exception as e:
        print("route fetch failed:", e, file=sys.stderr)
    latest = {"name": a.get("name") or "Run", "start": a["start_date_local"][:16],
              "miles": a["distance"] / MI, "moving_s": int(a.get("moving_time") or 0),
              "avg_hr": int(a.get("average_heartrate") or 0),
              "elev_ft": round((a.get("total_elevation_gain") or 0) * 3.28084),
              "latlng": latlng}

# ---- longest run per week, last 8 weeks (Mon-start)
monday = today - dt.timedelta(days=today.weekday())
weeks = []
for i in range(7, -1, -1):
    ws = monday - dt.timedelta(weeks=i)
    we = ws + dt.timedelta(days=7)
    mins = [int((r.get("moving_time") or 0) / 60) for r in runs
            if ws.isoformat() <= r["start_date_local"][:10] < we.isoformat()]
    weeks.append({"week": ws.strftime("%b %-d"), "min": max(mins, default=0)})

# ---- inspiration
year = str(today.year)
ly_day = today.replace(year=today.year - 1).isoformat()
ly_runs = [r for r in runs if r["start_date_local"][:10] == ly_day]
last_year = None
if ly_runs:
    best = max(ly_runs, key=lambda r: r["distance"])
    last_year = {"miles": sum(r["distance"] for r in ly_runs) / MI, "name": best.get("name") or "Run"}

lifetime = CFG["lifetime_baseline_miles"] + sum(
    r["distance"] for r in runs if r["start_date_local"][:10] >= CFG["lifetime_baseline_through"]) / MI

week_tot = {}
for r in runs:
    if r["start_date_local"][:4] != year:
        continue
    d = dt.date.fromisoformat(r["start_date_local"][:10])
    wk = d - dt.timedelta(days=d.weekday())
    week_tot[wk] = week_tot.get(wk, 0) + r["distance"] / MI
yr_runs = [r for r in runs if r["start_date_local"][:4] == year]
bests = []
if week_tot:
    wk, mi = max(week_tot.items(), key=lambda kv: kv[1])
    bests.append((f"biggest week ({wk.strftime('%b %-d')})", f"{mi:.1f} mi"))
if yr_runs:
    lr = max(yr_runs, key=lambda r: r["distance"])
    bests.append((f"longest run ({dt.date.fromisoformat(lr['start_date_local'][:10]).strftime('%b %-d')})",
                  f"{lr['distance'] / MI:.1f} mi"))
    bests.append(("runs this year", str(len(yr_runs))))

lines = CFG["lines"]
data = {
    "today": today.isoformat(), "now": now.strftime("%Y-%m-%dT%H:%M"),
    "goal_miles": CFG["goal_miles"], "daily": daily, "latest": latest,
    "race": {**CFG["race"], "long_runs": weeks},
    "inspo": {"last_year": last_year, "lifetime_miles": round(lifetime),
              "bests": bests, "line": lines[today.toordinal() % len(lines)]},
}
json.dump(data, sys.stdout)
