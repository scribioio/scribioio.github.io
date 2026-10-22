#!/usr/bin/env python3
"""Compute the CSP hashes for every inline script, style block, style
attribute and event-handler attribute in the site's HTML, and check that
_headers' Content-Security-Policy lists exactly those.

    python3 tools/csp-hashes.py           # check; exit 1 when _headers is stale
    python3 tools/csp-hashes.py --print   # print the directive values to paste

Run it after editing any page's inline <script>/<style>, a style="" or an
on*="" attribute: a changed inline block no longer matches its hash, and the
browser silently refuses it (styles vanish, the OAuth bounce stops).
"""
import base64, hashlib, html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADERS = ROOT / "_headers"

def h(text: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode() + "'"

def collect():
    scripts, styles, script_attrs, style_attrs = set(), set(), set(), set()
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts or "tools" in page.parts:
            continue
        src = page.read_text(encoding="utf-8")
        for m in re.finditer(r"<script(\s[^>]*)?>(.*?)</script>", src, re.S | re.I):
            attrs = m.group(1) or ""
            if "src=" in attrs:
                sys.exit(f"{page}: external <script src> found; add its origin to script-src by hand")
            scripts.add(h(m.group(2)))
        for m in re.finditer(r"<style(\s[^>]*)?>(.*?)</style>", src, re.S | re.I):
            styles.add(h(m.group(2)))
        for m in re.finditer(r"\son[a-z]+\s*=\s*\"([^\"]*)\"", src, re.I):
            script_attrs.add(h(html.unescape(m.group(1))))
        for m in re.finditer(r"\sstyle\s*=\s*\"([^\"]*)\"", src, re.I):
            style_attrs.add(h(html.unescape(m.group(1))))
    return scripts, styles, script_attrs, style_attrs

def main() -> int:
    scripts, styles, script_attrs, style_attrs = collect()
    want_script = sorted(scripts | script_attrs)
    want_style = sorted(styles | style_attrs)
    if "--print" in sys.argv:
        print("script-src hashes:", " ".join(want_script))
        print("style-src hashes:", " ".join(want_style))
        print("unsafe-hashes needed (script):", bool(script_attrs), "(style):", bool(style_attrs))
        return 0
    csp = next((l.split(":", 1)[1] for l in HEADERS.read_text().splitlines()
                if l.strip().lower().startswith("content-security-policy:")), None)
    if csp is None:
        print("_headers has no Content-Security-Policy"); return 1
    have = set(re.findall(r"'sha256-[A-Za-z0-9+/=]+'", csp))
    missing = (set(want_script) | set(want_style)) - have
    extra = have - (set(want_script) | set(want_style))
    for x in sorted(missing): print("MISSING", x)
    for x in sorted(extra): print("UNUSED ", x)
    if missing:
        return 1
    print(f"ok: {len(want_script)} script hashes, {len(want_style)} style hashes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
