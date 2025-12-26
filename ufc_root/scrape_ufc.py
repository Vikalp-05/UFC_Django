import json, re, requests
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