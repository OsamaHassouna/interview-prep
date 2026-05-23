# Bank Schema

Bank is split per topic: `bank/{topic}.json`. Each file is an object with a `questions` array. A manifest at `bank/_manifest.json` lists topics + counts (regenerated when bank changes).

## Topic files

```json
{
  "topic": "angular-core",
  "label": "Angular Core",
  "questions": [ Question, ... ]
}
```

## Question — MCQ (default)

```json
{
  "id": "ang-core-001",
  "topic": "angular-core",
  "difficulty": "L2",
  "mode": "mcq",
  "xp": 25,
  "tags": ["signals", "angular-17+"],
  "question": "Question text.",
  "options": [
    { "id": "a", "text": "option text" },
    { "id": "b", "text": "option text" },
    { "id": "c", "text": "option text" },
    { "id": "d", "text": "option text" }
  ],
  "correct": "a",
  "explanations": {
    "a": "Why a is correct.",
    "b": "Why b is wrong.",
    "c": "Why c is wrong.",
    "d": "Why d is wrong."
  },
  "year": 2025,
  "source": "https://..."
}
```

## Question — open / design / behavioral (senior+ L4+ mostly)

```json
{
  "id": "sysdesign-003",
  "topic": "fe-system-design",
  "difficulty": "L4",
  "mode": "open",
  "xp": 100,
  "question": "Design a dashboard with 50 widgets...",
  "model_answer_key_points": [
    "OnPush + per-widget data service",
    "Virtualization for off-screen widgets",
    "Profile-first, no premature optimization"
  ],
  "year": 2025,
  "source": "..."
}
```

For `mode: "behavioral"` add `model_answer_structure: "STAR..."`.
For `mode: "code"` add `snippet: "..."`.
For `mode: "design"` same shape as `open`.

## Difficulty → XP

| Difficulty | XP |
|------------|----|
| L1         | 10 |
| L2         | 25 |
| L3         | 50 |
| L4         | 100 |
| L5         | 200 |

## Guided Paths (v2.1+)

Optional `paths` block at the root of `bank/v2.json` defines leveled learning paths. Questions opt into a path with three extra fields: `path`, `level`, `order` — all otherwise ordinary MCQs that are excluded from the normal modes (Daily / Drill / Boss / Mock) so they only appear in Guided Path mode.

```json
"paths": {
  "forms-http-v1": {
    "label": "Forms + API",
    "subtitle": "...",
    "emoji": "📈",
    "passThreshold": 0.8,
    "levels": [
      {
        "level": 1,
        "title": "Reactive form basics",
        "summary": "...",
        "practical": {
          "title": "...",
          "scenario": "...",
          "hints": ["...", "..."],
          "solution": "```ts\n...\n```"
        }
      }
    ]
  }
}
```

A question opts in by adding:

```json
{ "path": "forms-http-v1", "level": 3, "order": 2, ... }
```

### Gate

Pass = `correct / total >= path.passThreshold` for the level's questions. On pass the user picks: **Advance**, **Repeat**, or **See practical example**. On fail: Repeat or Practical only.

## ID prefixes

| Topic                 | Prefix       |
|-----------------------|--------------|
| angular-core          | ang-core     |
| rxjs                  | rxjs         |
| change-detection-perf | cd-perf      |
| state-management      | state        |
| forms                 | forms        |
| typescript            | ts           |
| css-a11y              | css          |
| fe-system-design      | sysdesign    |
| code-debug            | debug        |
| behavioral            | behave       |
| ai-tooling-fe         | ai-fe        |
