"""
scrape_ai_papers.py — End-to-end scraper for weekly "top AI papers" digests
(strict "top-ai" filter). Writes ai_papers_top_ai_only.{csv,json} and caches
raw HTML under raw_html/.
"""

import os, re, time, json
from urllib.parse import urljoin, urlparse, urlunparse, urlencode, parse_qs
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import pandas as pd
from dateutil import parser as dateparser
from tqdm import tqdm
import xml.etree.ElementTree as ET

# ---------------- CONFIG ----------------
START_URL = "https://nlp.elvissaravia.com/t/ai"
OUT_CSV = "ai_papers_top_ai_only.csv"
OUT_JSON = "ai_papers_top_ai_only.json"
RAW_HTML_DIR = "raw_html"
USER_AGENT = "Mozilla/5.0 (compatible; AI-Papers-TopAI-Scraper/1.0)"
REQUESTS_TIMEOUT = 18
SLEEP = 0.6
MAX_RETRIES = 3
MAX_DISCOVER_PAGES = 400

os.makedirs(RAW_HTML_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})

# ---------------- Helpers ----------------
def safe_get(url, tries=MAX_RETRIES):
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=REQUESTS_TIMEOUT)
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt + 1 == tries:
                raise
            time.sleep(1 + attempt)
    raise RuntimeError("unreachable")

def absolutize(base, href):
    if not href: return None
    href = href.strip()
    if href.startswith('#'): return None
    if bool(urlparse(href).netloc):
        return href
    return urljoin(base, href)

def normalize_url_for_dedupe(u):
    if not u: return u
    p = urlparse(u)
    qs = parse_qs(p.query, keep_blank_values=True)
    for k in list(qs.keys()):
        if k.lower().startswith('utm_') or k.lower() in ('fbclid','gclid','mc_cid','mc_eid'):
            qs.pop(k, None)
    new_query = urlencode([(k,v) for k,vals in qs.items() for v in vals])
    normalized = urlunparse((p.scheme, p.netloc, p.path.rstrip('/'), '', new_query, ''))
    return normalized

def normalize_title(t):
    if not t: return ""
    s = t.lower()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^\w\s]', '', s)
    return s.strip()

def clean_noise_lines(text):
    if not text: return ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    keep=[]
    for ln in lines:
        if re.fullmatch(r'(?i)(share|like|subscribe|discussion about this post|by elvis|restacks?|likes?)', ln):
            continue
        if re.fullmatch(r'^\d{1,4}$', ln):
            continue
        keep.append(ln)
    return "\n".join(keep).strip()

def pick_canonical(links, base_url):
    if not links: return "", ""
    abs_links = [(absolutize(base_url, h), t) for h,t in links if h]
    for h,t in abs_links:
        if t and re.fullmatch(r'\s*Paper\s*', t, re.I):
            return h,t
    for h,t in abs_links:
        if t and re.search(r'\bpaper\b', t, re.I):
            return h,t
    for h,t in abs_links:
        if h and re.search(r'arxiv\.org|doi\.org|\.pdf', h, re.I):
            return h,t
    for h,t in abs_links:
        if h and not re.search(r'(elvissaravia\.com|nlp\.elvissaravia|substack\.com)', h, re.I):
            return h,t
    return abs_links[0] if abs_links else ("","")

# ---------------- Discovery (sitemap/rss/deep crawl) ----------------
def discover_weekly_top_ai(start_url, max_pages=MAX_DISCOVER_PAGES, sleep=SLEEP):
    candidates=[]
    seen=set()
    base = start_url.rstrip('/')
    parsed_base = urlparse(base)
    origin = f"{parsed_base.scheme}://{parsed_base.netloc}"

    def add(u):
        if not u: return
        try:
            u2 = absolutize(origin, u)
        except Exception:
            u2 = u
        n = normalize_url_for_dedupe(u2)
        if not n or n in seen: return
        seen.add(n); candidates.append(n)

    # 1) try sitemaps
    for sitemap_path in ("/sitemap.xml", "/sitemap_index.xml","/sitemap-index.xml"):
        try:
            r = session.get(origin + sitemap_path, timeout=REQUESTS_TIMEOUT)
            if r.status_code == 200 and r.text:
                try:
                    root = ET.fromstring(r.text)
                    for loc in root.iter():
                        if loc.tag.lower().endswith('loc') and loc.text:
                            add(loc.text.strip())
                except Exception:
                    for m in re.finditer(r'<loc>(.*?)</loc>', r.text, re.I|re.S):
                        add(m.group(1).strip())
        except Exception:
            pass

    # 2) try RSS / feed
    for feed_path in ("/feed", "/feed.xml", "/rss"):
        try:
            r = session.get(origin + feed_path, timeout=REQUESTS_TIMEOUT)
            if r.status_code == 200 and r.text:
                try:
                    root = ET.fromstring(r.text)
                    for item in root.iter():
                        if item.tag.lower().endswith('link') and item.text and item.text.strip().startswith('http'):
                            add(item.text.strip())
                except Exception:
                    for m in re.finditer(r'<item>.*?<link>(.*?)</link>.*?</item>', r.text, re.S|re.I):
                        add(m.group(1).strip())
        except Exception:
            pass

    # 3) deep crawl if few candidates found
    if len(candidates) < 60:
        to_visit=[start_url]
        visited=set()
        pages_visited=0
        while to_visit and pages_visited < max_pages:
            url = to_visit.pop(0)
            if url in visited: continue
            visited.add(url)
            pages_visited += 1
            try:
                r = session.get(url, timeout=REQUESTS_TIMEOUT)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
            except Exception:
                continue
            for a in soup.find_all("a", href=True):
                href = absolutize(url, a['href'])
                if not href: continue
                add(href)
                txt = (a.get_text(" ", strip=True) or "").lower()
                if any(k in txt for k in ("older", "next", "page", "archive", "older posts", "show more", "load more")):
                    if href not in visited and href not in to_visit:
                        to_visit.append(href)
                p = urlparse(href)
                if p.netloc == parsed_base.netloc and re.search(r'(page|archive|/t/|papers-of-the-week|top-ai-papers|ai-papers|/tag/)', p.path, re.I):
                    if href not in visited and href not in to_visit:
                        to_visit.append(href)
            time.sleep(sleep)

    # 4) STRICT filter: only keep URLs containing "top-ai"
    filtered = [u for u in candidates if "top-ai" in (u.lower() or "")]
    # fallback: if none matched, keep same-host candidates (should not happen)
    if not filtered:
        filtered = [u for u in candidates if urlparse(u).netloc == parsed_base.netloc]

    # final dedupe & preserve order
    final=[]; s=set()
    for u in filtered:
        n = normalize_url_for_dedupe(u)
        if n in s: continue
        s.add(n); final.append(n)
    return final

# ---------------- Post parsing ----------------
def extract_post_title_and_date(soup):
    title_tag = soup.find("h1")
    post_title = title_tag.get_text(" ", strip=True) if title_tag else (soup.title.get_text(" ", strip=True) if soup.title else "")
    display_date = ""
    parsed_iso = ""
    if title_tag:
        sib = title_tag.next_sibling
        while sib and not isinstance(sib, Tag):
            sib = sib.next_sibling
        if isinstance(sib, Tag):
            txt = sib.get_text(" ", strip=True)
            m = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b[^\n,]{0,20}\d{1,2},?\s*\d{4}', txt, re.I)
            if m:
                display_date = m.group(0).strip()
                try:
                    parsed_iso = dateparser.parse(display_date, fuzzy=True).date().isoformat()
                except Exception:
                    parsed_iso = ""
    if not display_date:
        time_tag = soup.find("time")
        if time_tag:
            display_date = time_tag.get_text(" ", strip=True)
            dt = time_tag.get("datetime") or display_date
            try:
                parsed_iso = dateparser.parse(dt, fuzzy=True).date().isoformat()
            except Exception:
                parsed_iso = ""
    if not display_date:
        visible = soup.get_text("\n", strip=True).splitlines()
        for ln in visible[:80]:
            m = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b[^\n,]{0,20}\d{1,2},?\s*\d{4}', ln, re.I)
            if m:
                display_date = m.group(0).strip()
                try:
                    parsed_iso = dateparser.parse(display_date, fuzzy=True).date().isoformat()
                except Exception:
                    parsed_iso = ""
                break
    return post_title, display_date, parsed_iso

def find_content_container(soup):
    for sel in ("article", ".post", ".post-content", ".entry-content", ".content", ".body"):
        el = soup.select_one(sel)
        if el: return el
    return soup.body or soup

def extract_links_from_nodes(nodes, base_url):
    links=[]
    for node in nodes:
        if isinstance(node, Tag):
            for a in node.find_all("a", href=True):
                links.append((a['href'], a.get_text(" ", strip=True)))
    return [(absolutize(base_url,h),t) for h,t in links]

def get_text_from_nodes(nodes):
    parts=[]
    for node in nodes:
        if isinstance(node, Tag):
            txt = node.get_text("\n", strip=True)
            if txt: parts.append(txt)
        elif isinstance(node, NavigableString):
            s = str(node).strip()
            if s: parts.append(s)
    return "\n\n".join(parts).strip()

def find_numbered_headings(container):
    candidates=[]
    for tagname in ("h1","h2","h3","h4","p","div","strong","b"):
        for el in container.find_all(tagname):
            if el.find_parent("li"): continue
            txt = el.get_text(" ", strip=True)
            if not txt: continue
            m = re.match(r'^\s*(\d+)\.\s+(.+)', txt)
            if m:
                rank = int(m.group(1)); raw_title = m.group(2).strip()
                n = normalize_title(raw_title)
                candidates.append((el, n, rank, raw_title))
    seen=set(); ordered=[]
    for el,n,rank,raw in candidates:
        if n in seen: continue
        seen.add(n); ordered.append((el,n,rank,raw))
    return ordered

def parse_post_into_papers(soup, post_url):
    container = find_content_container(soup)
    items=[]
    ol = container.find("ol")
    if ol:
        lis = ol.find_all("li", recursive=False)
        for idx, li in enumerate(lis, start=1):
            title=""
            for tagname in ("h1","h2","h3","h4","strong","b"):
                t = li.find(tagname)
                if t and t.get_text(strip=True):
                    title = re.sub(r'^\s*\d+\.\s*', '', t.get_text(" ", strip=True)).strip()
                    break
            if not title:
                first = li.get_text("\n", strip=True).splitlines()[0]
                title = re.sub(r'^\s*\d+\.\s*', '', first).strip()
            paras = [p.get_text(" ", strip=True) for p in li.find_all("p", recursive=False)]
            if paras and title and paras[0].lower().startswith(title.lower()[:min(40,len(title))]):
                paras = paras[1:]
            summary = clean_noise_lines("\n\n".join(paras)) or clean_noise_lines(li.get_text("\n", strip=True).replace(title,"",1))
            links = [(a['href'], a.get_text(" ", strip=True)) for a in li.find_all("a", href=True)]
            can, can_text = pick_canonical(links, post_url)
            items.append({"paper_rank": idx, "paper_title": title, "paper_summary": summary, "paper_link": can, "paper_link_text": can_text})
    else:
        headings = find_numbered_headings(container)
        if headings:
            heading_elems = [h[0] for h in headings]
            for el, norm, rank, raw_title in headings:
                summary_nodes=[]
                sib = el.next_sibling
                while sib is not None:
                    if isinstance(sib, Tag) and any(sib is he for he in heading_elems):
                        break
                    if isinstance(sib, Tag):
                        sfirst = sib.get_text(" ", strip=True)[:200].lower()
                        if re.search(r'message from the editor|subscribe to ai newsletter|subscribe|discussion about this post', sfirst):
                            break
                    summary_nodes.append(sib)
                    if isinstance(sib, Tag):
                        anchor_texts = " ".join([a.get_text(" ", strip=True) for a in sib.find_all("a", href=True)])
                        if re.search(r'\bPaper\b', anchor_texts, re.I) and re.search(r'\bTweet\b', anchor_texts, re.I):
                            break
                    sib = sib.next_sibling
                raw_summary = get_text_from_nodes(summary_nodes)
                summary = clean_noise_lines(raw_summary)
                links = extract_links_from_nodes(summary_nodes, post_url)
                can, can_text = pick_canonical(links, post_url) if links else ("","")
                items.append({"paper_rank": rank, "paper_title": raw_title, "paper_summary": summary, "paper_link": can, "paper_link_text": can_text})
        else:
            anchors = []
            for a in container.find_all("a", href=True):
                if re.search(r'\bPaper\b', a.get_text(" ", strip=True), re.I):
                    anchors.append(a)
            for idx,a in enumerate(anchors[:50], start=1):
                title = ""
                prev = a.previous_sibling; steps=0
                while prev is not None and steps < 8:
                    if isinstance(prev, Tag):
                        ttxt = prev.get_text(" ", strip=True)
                        if ttxt and len(ttxt) < 400:
                            title = ttxt; break
                    elif isinstance(prev, NavigableString):
                        ttxt = str(prev).strip()
                        if ttxt:
                            title = ttxt; break
                    prev = prev.previous_sibling; steps += 1
                href = absolutize(post_url, a['href'])
                items.append({"paper_rank": idx, "paper_title": title, "paper_summary": "", "paper_link": href, "paper_link_text": a.get_text(" ", strip=True)})
    # dedupe by normalized title (keep first)
    unique=[]; seen_titles=set()
    for it in items:
        n = normalize_title(it.get("paper_title",""))
        if not n:
            unique.append(it); continue
        if n in seen_titles: continue
        seen_titles.add(n); unique.append(it)
    # supplement if fewer than 10 from textual numbered chunks
    if len(unique) < 10:
        raw = container.get_text("\n", strip=False)
        pattern = re.compile(r'^\s*(\d+)\.\s+', re.MULTILINE)
        matches = list(pattern.finditer(raw))
        textual=[]
        for i,m in enumerate(matches):
            start = m.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(raw)
            chunk = raw[start:end].strip()
            firstline = chunk.splitlines()[0]
            mm = re.match(r'^\s*(\d+)\.\s*(.+)', firstline)
            title = mm.group(2).strip() if mm else ""
            summary = "\n".join(chunk.splitlines()[1:]).strip()
            textual.append({"paper_title": title, "paper_summary": clean_noise_lines(summary)})
        existing = set(normalize_title(x.get("paper_title","")) for x in unique if x.get("paper_title"))
        for t in textual:
            if len(unique) >= 10: break
            nt = normalize_title(t["paper_title"])
            if not nt or nt in existing: continue
            unique.append({"paper_rank": None, "paper_title": t["paper_title"], "paper_summary": t["paper_summary"], "paper_link": "", "paper_link_text": ""})
            existing.add(nt)
    final=[]
    for i,it in enumerate(unique[:10], start=1):
        final.append({
            "paper_rank": i,
            "paper_title": it.get("paper_title",""),
            "paper_summary": it.get("paper_summary",""),
            "paper_link": it.get("paper_link",""),
            "paper_link_text": it.get("paper_link_text","")
        })
    while len(final) < 10:
        final.append({"paper_rank": len(final)+1, "paper_title":"", "paper_summary":"", "paper_link":"", "paper_link_text":""})
    return final

# ---------------- Runner ----------------
def run_full_scrape_top_ai(start_url=START_URL):
    weekly_urls = discover_weekly_top_ai(start_url)
    print(f"Discovered {len(weekly_urls)} Top-AI weekly posts (showing up to 40):")
    for u in weekly_urls[:40]:
        print(" -", u)
    rows=[]
    for post_url in tqdm(weekly_urls, desc="Scraping weekly posts"):
        try:
            r = safe_get(post_url)
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print("WARN: failed fetch", post_url, e); continue
        # save raw html
        fname = os.path.join(RAW_HTML_DIR, re.sub(r'[^\w\-_\.]', '_', post_url)[:180] + ".html")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(r.text)
        post_title, post_date_display, post_date_iso = extract_post_title_and_date(soup)
        papers = parse_post_into_papers(soup, post_url)
        for p in papers:
            rows.append({
                "post_title": post_title,
                "post_date_display": post_date_display,
                "post_date_iso": post_date_iso,
                "post_url": post_url,
                "paper_rank": p.get("paper_rank"),
                "paper_title": p.get("paper_title",""),
                "paper_summary": p.get("paper_summary",""),
                "paper_link": p.get("paper_link",""),
                "paper_link_text": p.get("paper_link_text",""),
                "scraped_at": pd.Timestamp.now().isoformat()
            })
        time.sleep(SLEEP)
    if not rows:
        print("No rows scraped. Check discovery or connectivity.")
        return None
    df = pd.DataFrame(rows)
    df = df[["post_title","post_date_display","post_date_iso","post_url","paper_rank","paper_title","paper_summary","paper_link","paper_link_text","scraped_at"]]
    df.to_csv(OUT_CSV, index=False)
    df.to_json(OUT_JSON, orient="records", force_ascii=False, indent=2)
    print(f"Saved {len(df)} rows -> {OUT_CSV} and {OUT_JSON}")
    return df

# Execute
df = run_full_scrape_top_ai()

