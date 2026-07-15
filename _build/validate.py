#!/usr/bin/env python3
"""Validator for the HEATPROOF static output.

Checks:
  1. No broken internal links (every href to a local path resolves to a file).
  2. hreflang pairs are reciprocal (EN <-> zh) and x-default present.
  3. Every application page links to >=1 product.
  4. No duplicate canonical product routes.
  5. Application-temperature vs maximum-process-temperature are visually distinct on product pages.
  6. No Chinese characters leak into EN (non-/zh/) HTML output.
"""
import os, re, sys, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
warnings = []

# Collect all html files (skip _build, _docs, .git)
pages = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ('_build', '_docs', '.git', 'node_modules')]
    for fn in filenames:
        if fn.endswith('.html'):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            with open(full, encoding='utf-8') as f:
                pages[rel] = f.read()

print(f"Scanned {len(pages)} HTML pages")

def resolves(href):
    """Return True if an internal absolute href resolves to a file on disk."""
    href = href.split('#')[0].split('?')[0]
    if not href or not href.startswith('/'):
        return True  # external / anchor / relative — skip
    if href.startswith('//'):
        return True  # protocol-relative external
    p = href.lstrip('/')
    cand = os.path.join(ROOT, p)
    if os.path.isfile(cand):
        return True
    if os.path.isfile(os.path.join(cand, 'index.html')):
        return True
    # bare file (sitemap/robots/vercel)
    if os.path.isfile(os.path.join(ROOT, p)):
        return True
    return False

# ---- 1. broken links ----
href_re = re.compile(r'href="([^"]+)"')
for rel, txt in pages.items():
    for href in href_re.findall(txt):
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
            continue
        if not resolves(href):
            errors.append(f"[broken-link] {rel} -> {href}")

# ---- 2. hreflang reciprocity + x-default ----
hreflang_re = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"')
canon_re = re.compile(r'<link rel="canonical" href="([^"]+)"')
def path_of(url):
    return re.sub(r'^https?://[^/]+', '', url) or '/'
for rel, txt in pages.items():
    alts = dict((lang, path_of(u)) for lang, u in hreflang_re.findall(txt))
    if not alts:
        continue  # page without alternates (e.g. root home if not built here)
    canon_m = canon_re.search(txt)
    is_zh = rel.startswith('zh/')
    if 'x-default' not in alts:
        errors.append(f"[hreflang] {rel} missing x-default")
    if 'en' not in alts:
        errors.append(f"[hreflang] {rel} missing en alternate")
    # EN pages must carry a zh-Hans (or zh) alternate
    zh_keys = [k for k in alts if k.startswith('zh')]
    if not zh_keys:
        errors.append(f"[hreflang] {rel} missing zh alternate")
    # reciprocity: the en-alternate target must itself point back
    en_target = alts.get('en')
    if en_target:
        en_page = en_target.lstrip('/')
        en_file = os.path.join(ROOT, en_page, 'index.html') if not en_page.endswith('.html') else os.path.join(ROOT, en_page)
        if en_page == '':
            en_file = os.path.join(ROOT, 'index.html')
        if os.path.isfile(en_file):
            back = dict((l, path_of(u)) for l, u in hreflang_re.findall(open(en_file, encoding='utf-8').read()))
            for zk in zh_keys:
                zt = alts[zk]
                if back and zt not in back.values():
                    warnings.append(f"[hreflang-recip] {rel}: zh target {zt} not mirrored from en {en_target}")

# ---- 3. every application -> >=1 product link ----
prod_link_re = re.compile(r'href="(/products/(?:hp|3m|flexcon|biotech)-[^"/]+/)"')
for rel, txt in pages.items():
    if re.match(r'applications/[^/]+/[^/]+/index\.html$', rel) or re.match(r'industries/[^/]+/[^/]+/index\.html$', rel):
        if not prod_link_re.search(txt):
            # An application with the explicit "to be confirmed by sample" marker is an
            # intentional, flagged data gap (no HP product fits yet) — warn, don't error.
            if 'to be confirmed by sample' in txt or 'confirmed by sample' in txt:
                warnings.append(f"[app-pending-product] {rel} marked pending product selection")
            else:
                errors.append(f"[app-no-product] {rel} has no product link")

# ---- 4. duplicate canonical product routes ----
canon_seen = {}
for rel, txt in pages.items():
    if rel.startswith('products/hp-') and rel.endswith('index.html'):
        m = canon_re.search(txt)
        if m:
            c = path_of(m.group(1))
            if c in canon_seen:
                errors.append(f"[dup-canonical] {c} in {rel} and {canon_seen[c]}")
            canon_seen[c] = rel

# ---- 5. app-temp vs max-process-temp distinct on product pages ----
for rel, txt in pages.items():
    if rel.startswith('products/hp-') and rel.endswith('index.html'):
        has_app = 'Application temperature' in txt or 'Application Temperature' in txt
        has_max = 'Maximum process' in txt or 'Maximum Process' in txt or 'Max. Process' in txt
        # Rule: WHERE both temperatures are shown, they must be two distinct labeled cards.
        # Products with only one temperature in the data legitimately show one card.
        if has_app and has_max:
            # both present — confirm they are separate .tcard blocks (not merged)
            two = re.search(r'class="two">(.*?)</div></div></div>', txt, re.S)
            n_cards = txt.count('class="tcard"')
            if n_cards < 2:
                errors.append(f"[temp-merged] {rel}: both temps present but <2 tcards")

# ---- 6. Chinese leak in EN output ----
cjk = re.compile(r'[一-鿿]')
for rel, txt in pages.items():
    if rel.startswith('zh/'):
        continue
    # strip the hreflang/canonical link block and the EN<->ZH language switcher label
    # ("中文" is the legitimate switch-to-Chinese control on English pages)
    body = re.sub(r'<link rel="alternate"[^>]*>', '', txt)
    body = re.sub(r'<a class="lang"[^>]*>.*?</a>', '', body)
    if cjk.search(body):
        # show first offending line
        for i, line in enumerate(body.splitlines(), 1):
            if cjk.search(line):
                errors.append(f"[cjk-in-en] {rel}:{i}: {line.strip()[:80]}")
                break

# ---- report ----
print(f"\nERRORS: {len(errors)}")
for e in errors[:80]:
    print("  " + e)
print(f"\nWARNINGS: {len(warnings)}")
for w in warnings[:80]:
    print("  " + w)

sys.exit(1 if errors else 0)
