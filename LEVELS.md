# Game System Spec

## Player Levels

| Lv | Title         | XP threshold |
|----|---------------|--------------|
| 1  | Apprentice    | 0            |
| 2  | Practitioner  | 100          |
| 3  | Senior        | 300          |
| 4  | Staff         | 700          |
| 5  | Principal     | 1500         |
| 6  | Distinguished | 3000         |

## Question Difficulty → XP

| Difficulty | Label        | Base XP |
|------------|--------------|---------|
| L1         | Warm-up      | 10      |
| L2         | Standard     | 25      |
| L3         | Deep         | 50      |
| L4         | Stretch      | 100     |
| L5         | Boss-tier    | 200     |

## Grading

### MCQ
- **Correct** on first try → 100% XP
- **Wrong** → 0 XP, question goes into spaced repetition queue
- **Skipped** → 0 XP, no penalty, no SR queue change

### Open / code / design / behavioral
Self-grade after seeing model answer key points:
- **Full** (all key points covered, clear) → 100% XP
- **Strong** (most key points, minor gap) → 75% XP
- **Partial** (some key points, missing depth) → 40% XP
- **Wrong** → 0 XP, SR queue

Bonus: **Beyond model** (covers something the key points missed) → +25% XP.

## Streak (single session)

Consecutive Correct/Strong+Full answers:
- ≥ 3 → +10% XP per question
- ≥ 7 → +25% XP per question

Resets on Wrong or Partial.

## Mastery (per topic)

| Tier     | Requirement                                        |
|----------|----------------------------------------------------|
| Bronze   | 5 correct at L2+                                   |
| Silver   | 10 correct at L2+ incl. 3 at L3+                   |
| Gold     | Silver + 5 correct at L4+                          |
| Platinum | Gold + boss round 80%+                             |

## Spaced Repetition — Simple Bucket

Each question carries `srState`:
```
{ correctStreak: 0, lastSeenSession: 12, nextDueSession: 15, retired: false }
```

Rules:
- **Wrong** → `correctStreak = 0`, due in **3 sessions**
- **Partial** → `correctStreak = 0`, due in **7 sessions**
- **Correct (Strong/Full)** → `correctStreak += 1`, due in:
  - 1st correct: 7 sessions
  - 2nd correct: 14 sessions
  - 3rd correct: 21 sessions (mastered, can retire)
- **Mastered (3x correct in a row)** → `retired = true`, only re-surface in boss rounds

A "session" = one launch of the quiz UI / day. Counter increments on first question of a new day.

## Modes (UI)

- **Daily Practice** — pulls due Qs from SR queue first, then new Qs from weak-mastery topics
- **Topic Drill** — pick one topic, drill till exhausted or you tap out
- **Boss Round** — 10 mixed Qs from one topic. No skips. Bonus XP + badge on 80%+
- **Mock Interview** — 5 Qs across modes from a role preset (e.g. "Senior Angular @ fintech")
- **Guided Path** — leveled learning path (e.g. Forms + API). MCQ-only Qs grouped by level. Pass the level (>= `passThreshold`) to unlock the next level. After each level the user can view a practical example (scenario + reference solution). Path Qs are excluded from the other modes.

## Wrong-answer flow

1. User picks an option, submits.
2. UI reveals the correct answer + explanations for ALL options.
3. If wrong, the Q is flagged and queued (3 sessions).
4. User clicks "Got it" → next Q.
5. Wrong Qs accumulate in a "Review" view, sortable by topic + tag.
