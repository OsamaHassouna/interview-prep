# Interview Game

A single-file self-quiz tool for senior front-end interview prep. Two tracks — **UI** (CSS architecture, design tokens, scalable styling) and **Angular** (core, RxJS, change detection, state, forms, debug). Spaced repetition, XP / level / mastery, four play modes.

**Live:** https://interview-prep-oah.vercel.app/

## How it works

- Pick a mode: Daily Practice, Topic Drill, Boss Round, or Mock Interview.
- Answer multiple-choice questions sourced from real 2024–2026 interview material.
- Wrong answers reveal explanations for every option and re-queue for review.
- XP, streaks, and per-topic mastery (Bronze → Platinum) update as you play.
- Progress is stored in `localStorage`. No login, no backend, no tracking. Use **Export** on the Stats page to back up.

## Modes

| Mode | What it does |
|------|--------------|
| Daily Practice | Spaced-repetition queue first, then new Qs from your weakest topic |
| Topic Drill | Pick one topic, drill until you tap out |
| Boss Round | 10 mixed Qs from one topic. No skips. 80%+ earns a badge |
| Mock Interview | 5 mixed Qs from a track (UI or Angular). Sim the real thing |

## Run locally

It's one HTML file. Open it in a browser:

```
ui/index.html
```

That's it. No install, no build step at runtime.

## Editing the question bank

Questions live in `bank/v2.json`. After editing, re-bake them into the HTML:

```bash
python scripts/build-html.py
```

This injects the bank into the `<script id="bank-data">` block in `ui/index.html`.

## Tech

- Vanilla HTML + JS, no framework
- Tailwind CSS via CDN
- `localStorage` for persistence (export / import / reset built in)

## Repo layout

```
interview-prep/
├── ui/index.html       — the app (single file, deployable as-is)
├── bank/v2.json        — question bank (source of truth)
├── scripts/            — bank build + migration scripts
├── LEVELS.md           — XP / mastery / spaced-repetition spec
├── SCHEMA.md           — question JSON schema
└── archive/            — old seed material
```

## Deploying

Static site, deployable anywhere. For Vercel: import the repo, set **Root Directory** to `ui`, no build command needed.
