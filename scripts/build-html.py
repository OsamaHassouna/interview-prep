"""Inject bank/v1.json (or any bank JSON) into ui/index.html bank-data script block.

Run from anywhere: python scripts/build-html.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "bank" / "v2.json"
HTML = ROOT / "ui" / "index.html"

bank = json.loads(BANK.read_text(encoding="utf-8"))
new_data = {
    "topics": bank["topics"],
    "paths": bank.get("paths", {}),
    "questions": bank["questions"],
}
new_json = json.dumps(new_data, indent=2, ensure_ascii=False)

html = HTML.read_text(encoding="utf-8")
pattern = re.compile(
    r'<script id="bank-data" type="application/json">.*?</script>',
    re.DOTALL,
)
replacement = f'<script id="bank-data" type="application/json">\n{new_json}\n</script>'
# Use a lambda so re.sub does NOT interpret backslash escapes in the replacement
# (otherwise the \n inside JSON string values get converted to real newlines,
# producing invalid JSON.)
new_html, n = pattern.subn(lambda m: replacement, html, count=1)
if n != 1:
    raise SystemExit(f"Expected 1 replacement, got {n}")
HTML.write_text(new_html, encoding="utf-8")
paths = bank.get("paths", {})
print(f"Injected {len(bank['questions'])} questions across {len(bank['topics'])} topics + {len(paths)} guided path(s).")
