import json, re, os, requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://www.ufc.com"
RANKINGS_URL = "https://www.ufc.com/rankings"
TIMEOUT = 25
MAX_WORKERS = 8

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"

def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()

def norm(s):
    return re.sub(r"[^a-z]+", " ", (s or "").lower()).strip()

def write_json(data, filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def scrape_rankings():
    html = session.get(RANKINGS_URL, timeout=TIMEOUT).text
    soup = BeautifulSoup(html, "html.parser")

    rankings = {}

    for grp in soup.select("div.view-grouping"):
        info = grp.select_one("div.info")
        if not info:
            continue

        h4 = info.select_one("h4")
        wc = clean(h4.text) if h4 else None
        if not wc or "pound" in wc.lower():
            continue

        fighters = []

        champ = info.select_one("h5 a")
        if champ:
            fighters.append({
                "rank": "C",
                "name": clean(champ.text),
                "url": urljoin(BASE, champ.get("href", "")),
            })

        for row in grp.select("table tr"):
            rtd = row.select_one(".views-field-weight-class-rank")
            a = row.select_one(".views-field-title a")
            if not rtd or not a:
                continue

            m = re.search(r"\d+", clean(rtd.text))
            if not m:
                continue

            fighters.append({
                "rank": int(m.group()),
                "name": clean(a.text),
                "url": urljoin(BASE, a.get("href", "")),
            })

        rankings[wc] = (
            [f for f in fighters if f["rank"] == "C"] +
            sorted([f for f in fighters if f["rank"] != "C"], key=lambda x: x["rank"])
        )

    return rankings

def parse_profile(url):
    soup = BeautifulSoup(session.get(url, timeout=TIMEOUT).text, "html.parser")
    me = urlparse(url).path.strip("/").split("/")[-1].lower()
    
    out = {k: None for k in [
        "Age","Height","Weight","Reach","Leg Reach","Octagon Debut",
        "Fighting Style","Hometown","Record",
        "Striking Accuracy","Takedown Accuracy",
        "Significant Strike Defense","Takedown Defense",
        "Significant Strikes Landed","Significant Strikes Absorbed",
        "Takedown Average","Submission Average",
        "Last 3 Fights",
        "Fight 1","Date 1","End Round 1","Time 1","Method 1",
        "Fight 2","Date 2","End Round 2","Time 2","Method 2",
        "Fight 3","Date 3","End Round 3","Time 3","Method 3"
    ]}

    for row in soup.select(".c-bio__field"):
        lab = row.select_one(".c-bio__label")
        val = row.select_one(".c-bio__text")
        if not lab or not val:
            continue

        k = clean(lab.text).lower().rstrip(":")
        v = clean(val.text)

        if k == "age":
            m = re.search(r"\d+", v)
            out["Age"] = m.group(0) if m else None

        elif k == "height":
            m = re.search(r"\d+(?:\.\d+)?", v)
            if m:
                inches = int(round(float(m.group(0))))
                out["Height"] = f"{inches//12}'{inches%12}"

        elif k in ("reach", "leg reach"):
            m = re.search(r"\d+(?:\.\d+)?", v)
            if m:
                out["Reach" if k == "reach" else "Leg Reach"] = f"{int(round(float(m.group(0))))} in"

        elif k == "weight":
            m = re.search(r"\d+(?:\.\d+)?", v)
            out["Weight"] = f"{int(round(float(m.group(0))))} lb" if m else None

        elif k == "octagon debut":
            out["Octagon Debut"] = v

        elif k == "fighting style":
            out["Fighting Style"] = v

        elif k == "hometown":
            out["Hometown"] = v

    out["Fighting Style"] = out["Fighting Style"] or "MMA"

    m = re.search(r"(\d+)\s*-\s*(\d+)(?:\s*-\s*(\d+))?", soup.get_text(" "))
    if m:
        out["Record"] = f"{m.group(1)}-{m.group(2)}-{m.group(3) or 0}"

    cmap = {
        "sig str landed": "Significant Strikes Landed",
        "sig str absorbed": "Significant Strikes Absorbed",
        "takedown avg": "Takedown Average",
        "submission avg": "Submission Average",
        "sig str defense": "Significant Strike Defense",
        "takedown defense": "Takedown Defense",
    }
    for g in soup.select(".c-stat-compare__group"):
        lab = g.select_one(".c-stat-compare__label")
        if not lab:
            continue
        key = cmap.get(norm(lab.text))
        if not key:
            continue

        m = re.search(r"\d+(?:\.\d+)?", g.get_text(" "))
        if m:
            out[key] = m.group(0) + "%" if "Defense" in key else m.group(0)

    for t in soup.select("svg.e-chart-circle title"):
        txt = clean(t.text).lower()
        m = re.search(r"\d+(?:\.\d+)?", txt)
        if not m:
            continue
        if "striking accuracy" in txt:
            out["Striking Accuracy"] = m.group(0) + "%"
        elif "takedown accuracy" in txt:
            out["Takedown Accuracy"] = m.group(0) + "%"

    seq = []
    for card in soup.select(".c-card-event--athlete-results__matchup"):
        if len(seq) == 3:
            break
        win = (card.select_one(".win a[href]") or {}).get("href", "").lower()
        loss = (card.select_one(".loss a[href]") or {}).get("href", "").lower()
        if me in win:
            seq.append("W")
        elif me in loss:
            seq.append("L")
    out["Last 3 Fights"] = "".join(seq) or None

    for i, h in enumerate(soup.select(".c-card-event--athlete-results__headline")[:3], 1):
        names = [clean(a.text) for a in h.select("a") if clean(a.text)]
        out[f"Fight {i}"] = " vs ".join(names) if len(names) >= 2 else None

        date = h.find_next("div", class_="c-card-event--athlete-results__date")
        out[f"Date {i}"] = clean(date.text) if date else None

        def grab(lbl):
            lab = h.find_next("div", class_="c-card-event--athlete-results__result-label", string=lbl)
            if not lab:
                return None
            box = lab.find_parent("div", class_="c-card-event--athlete-results__result")
            val = box.select_one(".c-card-event--athlete-results__result-text") if box else None
            return clean(val.text) if val else None

        out[f"End Round {i}"] = grab("Round")
        out[f"Time {i}"] = grab("Time")
        out[f"Method {i}"] = grab("Method")

    return out

def main():
    rankings = scrape_rankings()

    urls = {f["url"] for fighters in rankings.values() for f in fighters}
    profiles = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(parse_profile, u): u for u in urls}
        for fut in as_completed(futures):
            url = futures[fut]
            profiles[url] = fut.result()

    for fighters in rankings.values():
        for f in fighters:
            f.update(profiles.get(f["url"], {}))

    write_json(rankings, "data/ufc.json")


if __name__ == "__main__":
    main()
