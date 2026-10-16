#!/usr/bin/env python3
"""Build the standalone HTML preview by inlining local assets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
index = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "styles.css").read_text(encoding="utf-8")
js = (ROOT / "app.js").read_text(encoding="utf-8")
firebase_config = (ROOT / "firebase-config.js").read_text(encoding="utf-8")

replacements = {
    '<link rel="stylesheet" href="/styles.css">': f"<style>\n{css}\n</style>",
    '  <script src="/firebase-config.js" defer></script>': f"  <script defer>\n{firebase_config}\n  </script>",
    '  <script src="/app.js" defer></script>': f"  <script defer>\n{js}\n  </script>",
}
for old, new in replacements.items():
    if old not in index:
        raise SystemExit(f"Expected asset reference not found: {old}")
    index = index.replace(old, new, 1)

(ROOT / "preview.html").write_text(index, encoding="utf-8")
print("Built preview.html with inline CSS, app.js, and Firebase Web App config.")
