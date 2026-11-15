#!/usr/bin/env python3
"""Lit les Google Docs publiés, range le texte par onglet / sous-onglet
et génère le site dans le dossier site/. Le texte n'est jamais modifié."""
import hashlib, json, re, shutil, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).parent
OUT = ROOT / "site"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
HEADS = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}
KEEP = {"font-weight", "font-style", "text-decoration", "vertical-align", "color",
        "background-color", "list-style-type", "content", "counter-reset",
        "counter-increment", "text-align"}


def norm(s):
    return re.sub(r"\W+", "", s.casefold().replace("l", "i"))


def text(el):
    return el.get_text(" ", strip=True)


def is_title(el):
    return (el.name in HEADS and not el.find(["img", "table", "ul", "ol"])
            and 0 < len(text(el)) <= 70)


def get_blocks(soup):
    root = soup.find(id="contents") or soup.find(class_="doc-content") or soup.body
    blocks = [c for c in root.children if getattr(c, "name", None)]
    while len(blocks) == 1 and blocks[0].name in ("div", "section"):
        blocks = [c for c in blocks[0].children if getattr(c, "name", None)]
    return blocks


def parse_tabs(blocks):
    """Un onglet commence par deux lignes de titre identiques (ou la 2e est le
    début de la 1re), comme dans l'export Google Docs."""
    tabs, cur, i = [], None, 0
    while i < len(blocks):
        b = blocks[i]
        if i + 1 < len(blocks) and is_title(b) and is_title(blocks[i + 1]):
            a, c = norm(text(b)), norm(text(blocks[i + 1]))
            if len(c) >= 2 and (a == c or a.startswith(c)):
                cur = {"title": text(b), "blocks": []}
                tabs.append(cur)
                i += 2
                continue
        if cur is not None:
            cur["blocks"].append(b)
        i += 1
    return tabs


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


def has_content(blocks):
    return any(b.get_text(strip=True) or b.find(["img", "table"]) for b in blocks)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "img").mkdir(parents=True)
    sess = requests.Session()
    sess.headers["User-Agent"] = "Mozilla/5.0"
    forced = {norm(x) for x in CFG["niveau1"]}
    nodes, articles, css, imgs = [], [], [], {}

    for d, doc in enumerate(CFG["documents"], 1):
        pre = f"d{d}"
        r = sess.get(doc["url"], timeout=60)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        css.append(filter_css("\n".join(s.get_text() for s in soup.find_all("style")), pre))
        tabs = parse_tabs(get_blocks(soup))
        if not tabs:
            sys.exit(f"Aucun onglet trouvé dans « {doc['nom']} »")
        stack, prev = [], None
        for n, t in enumerate(tabs):
            t["empty"] = not has_content(t["blocks"])
            if n == 0:
                lvl = 0
            elif norm(t["title"]) in forced:
                lvl = 1
            elif prev and prev["empty"]:
                lvl = prev["lvl"] + 1
            else:
                lvl = prev["lvl"]
            if n and lvl < 1 and tabs[0]["empty"]:
                lvl = 1
            lvl = min(lvl, len(stack))
            del stack[lvl:]
            node = {"id": len(nodes), "title": t["title"], "kids": [], "level": lvl,
                    "parent": stack[-1]["id"] if stack else None,
                    "has": not t["empty"]}
            if stack:
                stack[-1]["kids"].append(node["id"])
            nodes.append(node)
            html = "".join(clean_block(b, pre, doc["url"], sess, imgs) for b in t["blocks"])
            articles.append(f'<article id="a{node["id"]}" hidden>{html}</article>')
            stack.append(node)
            t["lvl"], prev = lvl, t
        print(f"{doc['nom']} : {len(tabs)} onglets")

    k = 0
    for n in nodes:
        if n["level"] == 0:
            n["hue"] = 255
        elif n["level"] == 1:
            n["hue"] = (k * 47 + 8) % 360
            k += 1
        else:
            n["hue"] = nodes[n["parent"]]["hue"]

    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y à %Hh%M")
    page = (tpl.replace("__DOCCSS__", "\n".join(css))
               .replace("__ARTICLES__", "\n".join(articles))
               .replace("__NODES__", json.dumps(nodes, ensure_ascii=False).replace("</", "<\\/"))
               .replace("__DATE__", now)
               .replace("__TITLE__", CFG["titre"]))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"Site généré : {len(nodes)} onglets, {len(imgs)} images")


if __name__ == "__main__":
    main()
