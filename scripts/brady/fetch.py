#!/usr/bin/env python3
"""Fetch a bradyid.com page with headless Chromium (Playwright) and dump rendered HTML.

Usage: python3 fetch.py <url> <output_file> [--wait-selector CSS] [--timeout MS]

bradyid.com blocks plain curl (403 / Akamai). This script uses a realistic UA +
viewport and waits for network idle (or an optional selector) before dumping HTML.
Sleeps 1.5s after load to be polite and let late XHRs settle.
Reuses one persistent browser is NOT done here (one-shot per invocation keeps it simple);
for batch crawling import fetch_many() instead.
"""
import sys
import time
import argparse

PLAYWRIGHT_CHROMIUM = "/opt/pw-browsers/chromium"
PROXY = __import__("os").environ.get("HTTPS_PROXY")  # env HTTPS_PROXY (agent proxy); CA is in system/NSS store
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")


def make_browser(p):
    # --ssl-version-max=tls1.2 is REQUIRED in this environment: the egress
    # gateway resets Chromium's TLS 1.3 ClientHello (curl/openssl are fine).
    kw = {"headless": True,
          "args": ["--no-sandbox", "--disable-gpu", "--ssl-version-max=tls1.2"]}
    if PROXY:
        kw["proxy"] = {"server": PROXY}
    try:
        return p.chromium.launch(**kw)
    except Exception:
        return p.chromium.launch(executable_path=PLAYWRIGHT_CHROMIUM, **kw)


def fetch_many(urls_outs, wait_selector=None, timeout=45000, delay=1.5):
    """urls_outs: list of (url, outfile_or_None). Returns list of (url, status, html)."""
    from playwright.sync_api import sync_playwright
    results = []
    with sync_playwright() as p:
        browser = make_browser(p)
        ctx = browser.new_context(user_agent=UA,
                                  viewport={"width": 1366, "height": 900},
                                  locale="en-US")
        page = ctx.new_page()
        for url, out in urls_outs:
            status = None
            html = ""
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                status = resp.status if resp else None
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                if wait_selector:
                    try:
                        page.wait_for_selector(wait_selector, timeout=10000)
                    except Exception:
                        pass
                time.sleep(delay)
                html = page.content()
            except Exception as e:
                html = ""
                sys.stderr.write(f"ERROR {url}: {e}\n")
            if out:
                with open(out, "w") as f:
                    f.write(html)
            results.append((url, status, html))
            sys.stderr.write(f"{status} {len(html)} {url}\n")
        browser.close()
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outfile")
    ap.add_argument("--wait-selector", default=None)
    ap.add_argument("--timeout", type=int, default=45000)
    args = ap.parse_args()
    res = fetch_many([(args.url, args.outfile)], wait_selector=args.wait_selector,
                     timeout=args.timeout)
    url, status, html = res[0]
    print(f"status={status} bytes={len(html)} -> {args.outfile}")
    if status and status >= 400:
        sys.exit(2)


if __name__ == "__main__":
    main()
