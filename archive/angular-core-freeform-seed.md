# Angular Core — Question Bank

> Format: each Q is a self-contained block. Frontmatter (HTML comment) holds metadata the skill reads. The skill picks Qs by topic + level + mode + re-ask queue.

---

<!--
id: ang-core-001
topic: angular-core
level: 2
mode: concept
xp: 25
tags: [signals, reactivity, angular-17+]
-->

## Q001 · L2 · concept · 25 XP

**Explain the difference between `signal()`, `computed()`, and `effect()`. When would you reach for each, and what's a common bug with `effect()`?**

<details>
<summary>Model Answer</summary>

- **`signal()`** — writable reactive primitive. The source of truth. `set()` / `update()` to mutate, call as function to read.
- **`computed()`** — derived signal. Lazy + memoized. Re-runs only when (a) a dependency it actually read changed, AND (b) the computed itself is read. Pure — no side effects.
- **`effect()`** — side-effect runner. Tracks signals it reads, re-runs after change detection. Use for syncing signals to non-Angular APIs (localStorage, third-party libs, logging). Should NOT mutate signals by default — `allowSignalWrites: true` is an escape hatch, not a pattern.

**Common bug:** writing to a signal inside an `effect()` that also reads it → infinite loop (or runtime error in strict mode). Solution: model it as a `computed()` instead, or split the read/write signals.

### Grading checklist
- [ ] signal = writable source of truth
- [ ] computed = derived + lazy + memoized + pure
- [ ] effect = side effects, runs after CD
- [ ] mention the "no writes in effect" guidance OR `allowSignalWrites` escape hatch
- [ ] name a real use case (localStorage sync, DOM API, analytics)

### Follow-ups
- How does Angular know which signals an `effect()` depends on?
- What happens if you call `signal()` outside an injection context?
- What's the difference between `computed()` and a getter that reads signals?
</details>

---

<!--
id: ang-core-002
topic: angular-core
level: 3
mode: concept
xp: 50
tags: [change-detection, onpush, signals, zoneless]
-->

## Q002 · L3 · concept · 50 XP

**A team is migrating an OnPush component tree to use signals. Walk through what actually triggers change detection in (a) a classic OnPush component with `@Input` + `async` pipe, vs (b) an OnPush component reading a `signal()`. What changes in a zoneless app?**

<details>
<summary>Model Answer</summary>

**Classic OnPush (a):**
- Input reference change → component marked dirty → CD runs on next tick.
- `async` pipe internally calls `markForCheck()` on emission → component dirty.
- DOM events bound in the template → mark ancestors dirty up to root.
- Manual `cdr.markForCheck()` / `detectChanges()`.
- Otherwise, CD is skipped for that subtree.

**Signal-based OnPush (b):**
- Reading a signal in the template registers a fine-grained dependency.
- Signal write → the specific view that read it is marked dirty (not the whole component necessarily — view-level granularity).
- No need for `async` pipe; signals plug directly into the template.
- CD still runs in a Zone tick, but only the dirty views update.

**Zoneless app:**
- No `NgZone` patching → no automatic CD on `setTimeout`, promises, XHR.
- Scheduler runs CD when:
  - A signal that a template reads changes
  - An event binding fires
  - `async` pipe emits
  - Manual `ApplicationRef.tick()` / `markForCheck()`
- Net effect: signals become the primary CD trigger; legacy code that relied on Zone catching async ops will silently stop updating.

### Grading checklist
- [ ] OnPush + Input: reference change triggers CD
- [ ] async pipe calls markForCheck on emission
- [ ] Signals provide view-level (not just component-level) dirty marking
- [ ] Zoneless removes Zone-driven CD; signal writes become primary trigger
- [ ] Mention legacy async (setTimeout/promise) won't trigger CD in zoneless

### Follow-ups
- What's the migration risk for a codebase full of `setTimeout` UI hacks going zoneless?
- How would you debug "my signal changed but the view didn't update"?
</details>

---

<!--
id: ang-core-003
topic: angular-core
level: 3
mode: code
xp: 50
tags: [rxjs, memory-leak, lifecycle]
-->

## Q003 · L3 · code · 50 XP

**What's wrong with this component? Identify all issues and rewrite the relevant parts.**

```ts
@Component({
  selector: 'app-feed',
  template: `<div *ngFor="let item of items">{{ item.name }}</div>`
})
export class FeedComponent implements OnInit {
  items: Item[] = [];

  constructor(private feed: FeedService, private route: ActivatedRoute) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.feed.load(params['id']).subscribe(data => {
        this.items = data;
      });
    });
  }
}
```

<details>
<summary>Model Answer</summary>

**Issues:**

1. **Memory leak — two unmanaged subscriptions.** `route.params` and the inner `feed.load()` are never unsubscribed. On route reuse / component destroy, they leak. Worse, the inner subscription is re-created on every param change but old ones stay alive.

2. **Race condition.** If params change fast (id=1 then id=2), the id=1 response can arrive *after* id=2 and overwrite the correct data. Classic nested-subscribe trap.

3. **Nested subscribes** — anti-pattern. Use a higher-order operator.

4. **No OnPush.** Not a bug per se, but a senior should default to OnPush.

5. **Missing trackBy** in `*ngFor` — perf issue at scale.

**Fix:**

```ts
@Component({
  selector: 'app-feed',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div *ngFor="let item of items(); trackBy: trackById">{{ item.name }}</div>
  `,
})
export class FeedComponent {
  private route = inject(ActivatedRoute);
  private feed  = inject(FeedService);

  items = toSignal(
    this.route.params.pipe(
      map(p => p['id']),
      switchMap(id => this.feed.load(id))
    ),
    { initialValue: [] as Item[] }
  );

  trackById = (_: number, item: Item) => item.id;
}
```

Or with `takeUntilDestroyed()` if staying with explicit subscribe.

### Grading checklist
- [ ] Identifies memory leak (no unsubscribe)
- [ ] Identifies race condition / nested subscribe
- [ ] Suggests `switchMap` (or `concatMap`/`exhaustMap` with reasoning)
- [ ] Uses `takeUntilDestroyed()` OR `toSignal()` OR `async` pipe to manage lifecycle
- [ ] Bonus: mentions OnPush + trackBy

### Follow-ups
- Why `switchMap` and not `mergeMap` here?
- When would `concatMap` be the right choice?
</details>

---

<!--
id: ang-core-004
topic: angular-core
level: 4
mode: design
xp: 100
tags: [architecture, performance, dashboards]
-->

## Q004 · L4 · design · 100 XP

**Design a dashboard that renders 50 independent widgets (charts, tables, KPIs). Each widget polls its own data on its own cadence. Users can drag/resize/rearrange. The current implementation runs CD on every widget every tick and the page is sluggish. What's your architecture?**

<details>
<summary>Model Answer</summary>

**Core principles:**
1. Isolate each widget's CD from the others.
2. Push data to widgets, don't pull through shared state.
3. Defer / virtualize off-screen widgets.

**Architecture:**

- **OnPush everywhere.** Default change detection only.
- **Widget contract:** each widget is a standalone component with `@Input() config` and gets data via a signal or observable injected from a per-widget data service. Widgets never touch shared global state.
- **Per-widget data streams.** A `WidgetDataService` (provided at widget level via `providers: []`, not root) owns polling + caching + retry for that widget. Polling uses `interval()` + `switchMap()` with `takeUntilDestroyed()`. Each widget can pause/resume.
- **CD isolation.** Each widget is its own view; with OnPush + signals, a widget's update doesn't trigger CD on siblings.
- **Virtualization.** Wrap the grid in a virtual viewport (CDK Virtual Scroll for lists, or IntersectionObserver-based "render only if visible" for arbitrary grids). Off-screen widgets are not rendered or paused from polling.
- **Drag/resize.** CDK Drag-Drop. Persist layout to a signal-based store, debounced write to backend. Drag handle outside the widget's reactive surface so dragging doesn't trigger widget CD.
- **Heavy widgets in workers.** Charts that crunch large datasets → Web Worker via `Comlink` for the transform, main thread only renders.
- **Routing.** Each dashboard view is a lazy-loaded route. Sub-route per "tab" if dashboards have tabs.
- **Observability.** Mark long-running widgets with `performance.mark()` so you can see in DevTools which one is the bottleneck.

**What I'd build first:** OnPush + per-widget service + virtualization. Workers + Comlink only if profiling proves chart cost dominates.

### Grading checklist
- [ ] OnPush + signal/observable per widget (CD isolation)
- [ ] Widget-scoped data service (not global state)
- [ ] Virtualization / IntersectionObserver for off-screen widgets
- [ ] Mentions trackBy / per-widget standalone component
- [ ] Profile-first mindset (don't pre-optimize workers)
- [ ] Bonus: takeUntilDestroyed, signal-based layout store, debounced persistence

### Follow-ups
- A widget needs data from another widget. How do you handle the coupling without re-globalizing state?
- One widget makes the whole tab sluggish. How do you diagnose?
</details>

---

<!--
id: ang-core-005
topic: angular-core
level: 2
mode: behavioral
xp: 25
tags: [STAR, complex-ui, leadership]
-->

## Q005 · L2 · behavioral · 25 XP

**Tell me about the most complex Angular UI you've built. What made it complex, what trade-offs did you make, and what would you do differently today?**

<details>
<summary>Model Answer (structure, not content)</summary>

Use **STAR**:
- **Situation** — context in 1–2 sentences. What product, why it mattered, scale (users, data, devs).
- **Task** — your specific role and what success looked like. Not "the team did X" — what *you* did.
- **Action** — 3–5 concrete decisions with reasoning. Architecture pattern, library trade-off, perf strategy, what you said no to. This is the meat.
- **Result** — measurable outcome (perf number, ship date, user impact, adoption). If you can't measure it, frame the qualitative outcome.

**Then close with reflection:** what you'd change today. Shows growth + current expertise.

### Grading checklist
- [ ] Picked a genuinely complex project (real scope, not "todo app with auth")
- [ ] Explained complexity dimension (scale / coupling / perf / coordination)
- [ ] At least 2 trade-offs with reasoning ("we chose X over Y because…")
- [ ] One concrete metric or outcome
- [ ] Reflection — what you'd change with current knowledge

### Follow-ups
- What was the biggest disagreement you had on that project and how did it resolve?
- If you had to rewrite it from scratch today with Angular 19+, what would you change?

### Prep note for Osama
Candidates: Tallam dashboards / Truelogy / Angular Deep Intelligence / Romoz / design-system-infrastructure. Pick the one with the clearest "complexity story" and a number attached.
</details>

---

<!-- END OF SEED SLICE - 5 questions. Expand to ~15 per topic in Phase 1. -->
