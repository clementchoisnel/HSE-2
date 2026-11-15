#!/usr/bin/env python3
"""Génère un site statique simple à partir de Google Docs."""
import hashlib, json, re, shutil, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
OUT = ROOT
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
KEEP = {"font-weight", "font-style", "text-decoration", "vertical-align", "color",
        "background-color", "list-style-type", "content", "counter-reset",
        "counter-increment", "text-align"}

def filter_css(css, pre):
    out = []
    for sel, body in re.findall(r"([^{}@]+)\{([^{}]*)\}", css):
        sel = sel.strip()
        if re.search(r"\b(body|html)\b|doc-content", sel):
            continue
        keep = []
        for decl in body.split(";"):
            if ":" not in decl:
                continue
            k, v = (x.strip() for x in decl.split(":", 1))
            lv = v.lower().replace(" ", "")
            if k not in KEEP:
                continue
            if k == "color" and lv in ("#000000", "#000", "black"):
                continue
            if k == "background-color" and lv in ("#ffffff", "#fff", "white", "transparent"):
                continue
            keep.append(f"{k}:{v}")
        if keep:
            s = re.sub(r"\.([A-Za-z_][\w-]*)", lambda m: f".{pre}-{m.group(1)}", sel)
            out.append(f"{s}{{{';'.join(keep)}}}")
    return "\n".join(out)

def fetch_img(src, base, sess, cache):
    src = urljoin(base, src)
    if src in cache:
        return cache[src]
    try:
        r = sess.get(src, timeout=60)
        r.raise_for_status()
        kind = r.headers.get("content-type", "").split(";")[0]
        ext = {"image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp",
               "image/svg+xml": ".svg"}.get(kind, ".png")
        name = "img/" + hashlib.sha1(src.encode()).hexdigest()[:16] + ext
        (OUT / name).write_bytes(r.content)
        cache[src] = name
    except Exception as e:
        print("Image non téléchargée :", e)
        cache[src] = src
    return cache[src]

def clean_block(el, pre, base, sess, imgs):
    for t in [el] + el.find_all(True):
        if t.get("class"):
            t["class"] = [f"{pre}-{c}" for c in t["class"]]
        if t.name != "img":
            t.attrs.pop("style", None)
        t.attrs.pop("id", None)
    for im in el.find_all("img"):
        if im.get("src"):
            im["src"] = fetch_img(im["src"], base, sess, imgs)
        for a in ("style", "width", "height", "srcset"):
            im.attrs.pop(a, None)
        im["loading"] = "lazy"
    for a in el.find_all("a", href=True):
        q = parse_qs(urlparse(a["href"]).query).get("q")
        if "google.com/url" in a["href"] and q:
            a["href"] = q[0]
        a["target"], a["rel"] = "_blank", "noopener"
    return str(el)

def main():
   img_dir = ROOT / "img"
    if img_dir.exists():
     shutil.rmtree(img_dir)
 img_dir.mkdir(parents=True, exist_ok=True)
    sess = requests.Session()
    sess.headers["User-Agent"] = "Mozilla/5.0"
    nodes, articles, css, imgs = [], [], [], {}

    for d, doc in enumerate(CFG["documents"], 1):
        pre = f"d{d}"
        r = sess.get(doc["url"], timeout=60)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        css.append(filter_css("\n".join(s.get_text() for s in soup.find_all("style")), pre))
        
        root = soup.find(id="contents") or soup.find(class_="doc-content") or soup.body
        html = "".join(clean_block(b, pre, doc["url"], sess, imgs) for b in root.children if getattr(b, "name", None))
        
        node = {"id": len(nodes), "title": doc["nom"], "kids": [], "level": 0, "parent": None, "has": True}
        nodes.append(node)
        articles.append(f'<article id="a{node["id"]}">{html}</article>')
        print(f"{doc['nom']} : importé avec succès")

    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y à %Hh%M")
    page = (tpl.replace("__DOCCSS__", "\n".join(css))
               .replace("__ARTICLES__", "\n".join(articles))
               .replace("__NODES__", json.dumps(nodes, ensure_ascii=False).replace("</", "<\\/"))
               .replace("__DATE__", now)
               .replace("__TITLE__", CFG["titre"]))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"Site généré avec succès !")

if __name__ == "__main__":
    main()
