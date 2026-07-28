"""Pre-fetch research sources for pending by-elections into research-cache/.

Run by the Thursday-night GitHub Action (unrestricted egress). The Friday
cloud agent has no outbound page access, so everything it needs to verify
a defending party must already be in the repo:
 - LEAP daily result pages (vacating councillor names + gain/hold notation)
 - Wikipedia council-election pages (the party each councillor was ELECTED
   under — the authoritative check; LEAP notation can reflect defections)
"""
import json, pathlib, re, time, urllib.parse, urllib.request

UA = {"User-Agent": "called-it-defenders-cache/1.0 (research pre-fetch)"}
ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "research-cache"

def get(url: str) -> str | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  miss: {url} ({e})")
        return None

def main() -> None:
    pending = json.loads((ROOT / "pending.json").read_text())
    (CACHE / "leap").mkdir(parents=True, exist_ok=True)
    (CACHE / "wikipedia").mkdir(parents=True, exist_ok=True)

    # LEAP daily pages, one per distinct poll date
    for date in sorted({p["pollDate"] for p in pending}):
        out = CACHE / "leap" / f"{date}.html"
        html = get(f"https://www.andrewteale.me.uk/leap/by/{date}/")
        if html:
            out.write_text(html)
            print(f"leap {date}: cached")
        time.sleep(1)

    # Wikipedia election pages per council: search for every
    # "<council> ... election" article and cache the raw wikitext
    for council in sorted({p["council"] for p in pending}):
        words = council.replace("-", " ")
        q = urllib.parse.quote(f'intitle:"{words}" intitle:"election"')
        search = get("https://en.wikipedia.org/w/api.php?action=query&list=search"
                     f"&srsearch={q}&srlimit=25&format=json")
        if not search:
            continue
        titles = [hit["title"] for hit in json.loads(search)["query"]["search"]
                  if re.search(r"\d{4}.*(council|Council).*election", hit["title"])]
        for title in titles:
            safe = re.sub(r"[^A-Za-z0-9_-]", "_", title)
            out = CACHE / "wikipedia" / f"{safe}.txt"
            raw = get("https://en.wikipedia.org/w/index.php?title="
                      f"{urllib.parse.quote(title)}&action=raw")
            if raw:
                out.write_text(raw)
                print(f"wikipedia: cached {title}")
            time.sleep(1)

main()
