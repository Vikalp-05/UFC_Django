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

def parse_profile(url):
    r = session.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    clean = lambda s: re.sub(r"\s+", " ", (s or "")).strip()
    norm  = lambda s: re.sub(r"[^a-z]+", " ", (s or "").lower()).strip()
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