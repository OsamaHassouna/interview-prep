"""Merge bank/v2-additions.json questions into bank/v2.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V2 = ROOT / "bank" / "v2.json"
ADDS = ROOT / "bank" / "v2-additions.json"

v2 = json.loads(V2.read_text(encoding="utf-8"))
adds = json.loads(ADDS.read_text(encoding="utf-8"))

existing_ids = {q["id"] for q in v2["questions"]}
new = [q for q in adds["questions"] if q["id"] not in existing_ids]
v2["questions"].extend(new)

V2.write_text(json.dumps(v2, indent=2, ensure_ascii=False), encoding="utf-8")

from collections import Counter
by_topic = Counter(q["topic"] for q in v2["questions"])
by_track = Counter(q["track"] for q in v2["questions"])
by_diff = Counter(q["difficulty"] for q in v2["questions"])
by_mode = Counter(q["mode"] for q in v2["questions"])

print(f"Merged {len(new)} new Qs. Total: {len(v2['questions'])}")
print(f"By track: {dict(sorted(by_track.items()))}")
print(f"By difficulty: {dict(sorted(by_diff.items()))}")
print(f"By mode: {dict(sorted(by_mode.items()))}")
print("By topic:")
for t, c in sorted(by_topic.items()):
    print(f"  {t}: {c}")
