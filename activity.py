#!/usr/bin/env python3
"""Genera assets/activity-v1.svg con el calendario de contribuciones real (GraphQL).
Uso: python3 activity.py [usuario]   (token: GITHUB_TOKEN o `gh auth token`)"""
import json, os, subprocess, sys, urllib.request
from datetime import date
from xml.sax.saxutils import escape as esc

USER = sys.argv[1] if len(sys.argv) > 1 else "CarlosNuBa"
OUT = "assets/activity-v1.svg"
BG, CARD, EDGE, TEXT, MUTED = "#0d1326", "#141b35", "#243056", "#e8ecff", "#8f9bc4"
LEVELS = ["#27325c", "#14532d", "#16a34a", "#34d399", "#a7f3d0"]
FONT = "'Segoe UI','Helvetica Neue',Arial,'DejaVu Sans',sans-serif"
Q = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions
weeks{contributionDays{date contributionCount}}}}}}"""


def token():
    t = os.environ.get("GITHUB_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql", method="POST",
        data=json.dumps({"query": Q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json", "User-Agent": "profile-activity"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in d:
        sys.exit(f"GraphQL: {d['errors']}")
    return d["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(n, mx):
    if n == 0:
        return 0
    return min(4, 1 + int(3 * (n - 1) / max(mx - 1, 1) + 0.0001)) if mx > 1 else 2


def streaks(days):
    best = cur = 0
    for d in days:
        cur = cur + 1 if d[1] > 0 else 0
        best = max(best, cur)
    now = 0
    for d in reversed(days):
        if d[1] > 0:
            now += 1
        elif d[0] != date.today().isoformat():
            break
    return now, best


def main():
    cal = fetch()
    weeks = cal["weeks"]
    days = [(x["date"], x["contributionCount"]) for w in weeks for x in w["contributionDays"]]
    mx = max([n for _, n in days] + [0])
    now, best = streaks(days)
    maxday = max(days, key=lambda x: x[1]) if days else ("-", 0)
    cs, gap, x0, y0 = 16, 4, 40, 100
    w = x0 * 2 + max(len(weeks), 53) * (cs + gap)
    w = max(w, 1200)
    h = 320
    b = f'<text x="40" y="52" font-size="22" font-weight="700" fill="{TEXT}">Actividad</text>'
    b += f'<text x="40" y="76" font-size="14" fill="{MUTED}">Contribuciones del último año · se actualiza cada día</text>'
    pad = max(0, 53 - len(weeks))
    for i in range(pad):
        for wd in range(7):
            b += f'<rect x="{x0 + i*(cs+gap)}" y="{y0 + wd*(cs+gap)}" width="{cs}" height="{cs}" rx="4" fill="{LEVELS[0]}"/>'
    for i, wk in enumerate(weeks, start=pad):
        for dd in wk["contributionDays"]:
            wd = date.fromisoformat(dd["date"]).isoweekday() % 7
            c = LEVELS[level(dd["contributionCount"], mx)]
            b += (f'<rect x="{x0 + i*(cs+gap)}" y="{y0 + wd*(cs+gap)}" width="{cs}" height="{cs}" rx="4" fill="{c}" opacity="0">'
                  f'<title>{dd["date"]}: {dd["contributionCount"]}</title>'
                  f'<animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{i*0.025:.2f}s" fill="freeze"/></rect>')
    ly = y0 + 7 * (cs + gap) + 22
    stats = [("TOTAL", str(cal["totalContributions"])), ("RACHA ACTUAL", f"{now} d"), ("MEJOR RACHA", f"{best} d"), ("MEJOR DÍA", str(maxday[1]))]
    for i, (k, v) in enumerate(stats):
        sx = 40 + i * 230
        b += f'<text x="{sx}" y="{ly}" font-size="12" fill="{MUTED}" letter-spacing="1.5">{k}</text>'
        b += f'<text x="{sx}" y="{ly+26}" font-size="24" font-weight="700" fill="{TEXT}">{esc(v)}</text>'
    lx = w - 40 - 5 * 24 - 70
    b += f'<text x="{lx}" y="{ly+16}" font-size="12" fill="{MUTED}">menos</text>'
    for i, c in enumerate(LEVELS):
        b += f'<rect x="{lx+48+i*22}" y="{ly+4}" width="16" height="16" rx="4" fill="{c}"/>'
    b += f'<text x="{lx+48+5*22+4}" y="{ly+16}" font-size="12" fill="{MUTED}">más</text>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" font-family="{FONT}" '
           f'aria-label="Actividad: {cal["totalContributions"]} contribuciones en el último año"><rect width="{w}" height="{h}" rx="18" fill="{BG}"/>'
           f'<rect x="8" y="8" width="{w-16}" height="{h-16}" rx="14" fill="{CARD}" stroke="{EDGE}" stroke-width="1.5"/>{b}</svg>')
    os.makedirs("assets", exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print("ok", OUT, cal["totalContributions"], "contribuciones")


main()
