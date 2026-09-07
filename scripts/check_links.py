#!/usr/bin/env python3
"""Check all pages on the local Hugo dev server for dead links."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import time

BASE = "http://localhost:1314/OSGEO-Hugo/"
PFX = "/OSGEO-Hugo/"

visited = set()
queue = [BASE]
broken = []
ext_cache = {}
int_cache = {}

session = requests.Session()
session.headers["User-Agent"] = "LinkChecker/1.0"

pc = 0
while queue:
    url = queue.pop(0)
    if url in visited:
        continue
    visited.add(url)
    p = urlparse(url)
    if p.hostname not in ("localhost", "127.0.0.1"):
        continue
    if not p.path.startswith(PFX):
        continue

    pc += 1
    try:
        r = session.get(url, timeout=10)
    except Exception:
        continue
    if r.status_code != 200:
        continue

    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h.startswith("#") or h.startswith("mailto:") or h.startswith("javascript:"):
            continue
        fu = urljoin(url, h)
        fp = urlparse(fu)

        if fp.hostname in ("localhost", "127.0.0.1"):
            clean = fp._replace(fragment="").geturl()
            if clean not in visited and fp.path.startswith(PFX):
                queue.append(clean)
            if clean not in int_cache:
                try:
                    c = session.head(clean, timeout=5, allow_redirects=True)
                    int_cache[clean] = c.status_code
                except Exception:
                    int_cache[clean] = "timeout"
            st = int_cache[clean]
            if (isinstance(st, int) and st >= 400) or st == "timeout":
                sp = p.path.replace(PFX, "/")
                lp = fp.path.replace(PFX, "/")
                broken.append((sp, lp, st))

        elif fp.scheme in ("http", "https"):
            if fu not in ext_cache:
                try:
                    time.sleep(0.12)
                    c = session.head(fu, timeout=10, allow_redirects=True)
                    if c.status_code == 405:
                        c = session.get(fu, timeout=10, allow_redirects=True)
                    ext_cache[fu] = c.status_code
                except Exception as e:
                    ext_cache[fu] = f"Err:{str(e)[:30]}"
            st = ext_cache[fu]
            if (isinstance(st, int) and st >= 400) or (isinstance(st, str) and st.startswith("Err")):
                sp = p.path.replace(PFX, "/")
                broken.append((sp, fu, st))

    if pc % 25 == 0:
        print(f"  [{pc} pages, {len(broken)} broken, {len(ext_cache)} ext]", file=sys.stderr, flush=True)

# Deduplicate
seen = set()
ub = []
for src, link, st in broken:
    k = (src, link)
    if k not in seen:
        seen.add(k)
        ub.append((src, link, st))

print(f"Pages crawled: {pc}")
print(f"External links checked: {len(ext_cache)}")
print(f"Broken links: {len(ub)}")
print()
if ub:
    print(f"| {'Source Page':<42} | {'Broken Link':<58} | {'Status':<8} |")
    print(f"|{'-'*44}|{'-'*60}|{'-'*10}|")
    for src, link, st in sorted(ub):
        print(f"| {src:<42} | {link[:56]:<58} | {str(st):<8} |")
else:
    print("No broken links found!")
