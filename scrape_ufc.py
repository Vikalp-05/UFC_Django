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