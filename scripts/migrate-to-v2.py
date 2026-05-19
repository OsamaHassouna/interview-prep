"""Migrate bank/v1.json to bank/v2.json with track field + new UI topics.

Changes:
- Add `track` field to every question ("ui" | "angular" | "both")
- Remove `css-a11y` as a topic
- Migrate the 3 css-a11y Qs into new homes:
  - container-queries Q  -> scalable-styling
  - focus-management Q   -> scalable-styling
  - :has() selector Q    -> css-architecture
- Add 3 new UI topics (css-architecture, design-tokens-systems, scalable-styling)
- Preserve all existing Qs

Run: python scripts/migrate-to-v2.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "bank" / "v1.json"
DST = ROOT / "bank" / "v2.json"

src = json.loads(SRC.read_text(encoding="utf-8"))

# new topics map
topics = {
    "angular-core":          { "label": "Angular Core" },
    "rxjs":                  { "label": "RxJS" },
    "change-detection-perf": { "label": "Change Detection & Perf" },
    "state-management":      { "label": "State Management" },
    "forms":                 { "label": "Forms" },
    "typescript":            { "label": "TypeScript" },
    "css-architecture":      { "label": "CSS Architecture" },
    "design-tokens-systems": { "label": "Design Tokens & Systems" },
    "scalable-styling":      { "label": "Scalable Styling" },
    "fe-system-design":      { "label": "FE System Design" },
    "code-debug":            { "label": "Code Debug" },
    "behavioral":            { "label": "Behavioral" },
    "ai-tooling-fe":         { "label": "AI Tooling for FE" },
}

# topic -> default track mapping
TRACK_BY_TOPIC = {
    "angular-core":          "angular",
    "rxjs":                  "angular",
    "change-detection-perf": "angular",
    "state-management":      "angular",
    "forms":                 "angular",
    "css-architecture":      "ui",
    "design-tokens-systems": "ui",
    "scalable-styling":      "ui",
    "typescript":            "both",
    "fe-system-design":      "both",
    "behavioral":            "both",
    "ai-tooling-fe":         "both",
    # code-debug: per-Q decision (Angular snippets -> angular, generic -> ui)
}

# code-debug Q-specific track overrides (existing Qs are all Angular-flavored)
CODE_DEBUG_TRACK = {
    "debug-001": "angular",  # nested subscribe leak
    "debug-002": "angular",  # signal effect loop
    "debug-003": "angular",  # OnPush mutation
    "debug-004": "angular",  # valueChanges no debounce
}

# migrate css-a11y questions to new topics
CSS_A11Y_REMAP = {
    "css-001": ("scalable-styling", "Container queries belong in scalable-styling now"),
    "css-002": ("scalable-styling", "Focus management is component-library concern"),
    "css-003": ("css-architecture", "`:has()` is selector strategy"),
}

new_questions = []
for q in src["questions"]:
    nq = dict(q)
    # remap css-a11y topic
    if nq["topic"] == "css-a11y":
        new_topic, _ = CSS_A11Y_REMAP[nq["id"]]
        nq["topic"] = new_topic
    # add track
    if nq["topic"] == "code-debug":
        nq["track"] = CODE_DEBUG_TRACK.get(nq["id"], "both")
    else:
        nq["track"] = TRACK_BY_TOPIC[nq["topic"]]
    new_questions.append(nq)

out = {
    "generated_at": "2026-05-13",
    "version": "v2-authored",
    "note": (
        "v2: added `track` field for two-track Mock Interview (ui / angular / both). "
        "Dropped css-a11y as a topic; questions absorbed into css-architecture and scalable-styling. "
        "Added 3 new senior UI-track topics: css-architecture, design-tokens-systems, scalable-styling. "
        "Senior framing throughout — no basics."
    ),
    "topics": topics,
    "questions": new_questions,
}

DST.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Migrated {len(new_questions)} questions to {DST.name}")
print(f"Track counts: ui={sum(1 for q in new_questions if q['track']=='ui')}, "
      f"angular={sum(1 for q in new_questions if q['track']=='angular')}, "
      f"both={sum(1 for q in new_questions if q['track']=='both')}")
