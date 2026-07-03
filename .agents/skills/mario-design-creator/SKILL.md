---
name: mario-design-creator
description: >-
  Interactively author a new design doc from scratch, gathering the author's
  input section by section and gating progress on mario-design-reviewer's
  checklist — never advancing to the next section or phase until the current
  one is fully met (or the user explicitly says to bypass). Use whenever the
  user wants to write, start, or draft a design doc, high-level design, or
  goals doc from the ground up — even if they say "help me write a design
  doc", "let's start a new design", "create a design doc for X", or "walk me
  through the design review process for this." Produces a single markdown
  file following the bundled design doc template.
compatibility: >-
  Hard dependency on the mario-design-reviewer skill (invoked via the Skill
  tool) for checklist-driven gating — do not use this skill if
  mario-design-reviewer is unavailable. Uses references/design-doc-template.md
  as the canonical document skeleton, and Write/Edit to create and update the
  doc file on disk.
metadata:
  author: mario
  version: "1.0"
  category: document-authoring
---

# Design Doc Creator

Interactively author a design doc, one section at a time, following the same
design review process that `mario-design-reviewer` grades against — so the
doc that comes out the other end is review-ready by construction, not by
luck.

---

## The rule

**Never advance past a gate that hasn't been satisfied.** A gate is
satisfied one of two ways:

1. **Content gate** — invoke the `mario-design-reviewer` skill against the
   current draft file, and the relevant checklist row(s) come back
   `✅ Met` or `N/A`.
2. **Process gate** — the user directly confirms the real-world action
   happened (a review meeting was held, allies were consulted, etc.) —
   `mario-design-reviewer` can't see this from the file alone, so ask
   directly.

If a gate isn't satisfied, don't move on — help the user close the gap (ask
a targeted follow-up, revise the draft, re-check), and loop until it passes.

**The only way to skip a gate is if the user explicitly says so** — "skip
this," "bypass the review," "let's move on anyway," something unambiguous.
Silence, a topic change, or you inferring urgency does not count as
permission. When a gate is bypassed, write a plain note into the doc (e.g.
under Risks and Open Questions) saying what was skipped and that it was an
explicit author override — don't silently hide the gap.

---

## Step 1: Set up

Ask, in one message:

1. **What are we designing?** — a sentence or two is enough to seed the
   Problem section.
2. **Where should the file live?** — default to `./designs/<slug-of-title>.md`
   if the user doesn't care; otherwise use the path they give. Create parent
   directories as needed. If the file already exists, don't overwrite it —
   see Gotchas on resuming.

Read [references/design-doc-template.md](references/design-doc-template.md)
in full — this is the skeleton every doc follows in this skill. Create the
file at the chosen path with the template's headings in place, then start
replacing guidance text with real content, section by section, in the
phases below.

---

## Step 2: Work the phases in order

Work through the phases below in order. Within a phase, work through its
sections in order. Do not skip a section, phase, or gate without meeting its
condition (see The Rule).

```
- [ ] Phase 1: Goals Doc (Problem → Challenges → Customer Experience → Goals/Non-Goals → Constraints → Glossary → Key Allies) (GATE: content + process)
- [ ] Phase 2: Design Doc (Strategy → Common Considerations → Cost → API → Risks → Acknowledgements) (GATE: content + process)
- [ ] Phase 3: Implementation (Schedule → Blockers → Diagrams) (GATE: process)
- [ ] Phase 4: Finalize (full checklist run + report)
```

### Phase 1 — Goals Doc

Ask for, and write into the file, one section at a time, in this order:

| # | Section | Checklist row |
| - | ------- | -------------- |
| 1 | Problem | #1 |
| 2 | Challenges | #6 |
| 3 | Customer Experience | #2 |
| 4 | Goals | #3 |
| 5 | Non-Goals | #4 |
| 6 | Constraints *(skip if no numeric requirements — mark N/A, don't force one)* | #5 |
| 7 | Glossary *(skip if no jargon/acronyms — not checklist-graded)* | — |
| 8 | Key Allies | #7 |

After each section, invoke the `mario-design-reviewer` skill on the file and
check **only that row's Status**:

- `✅ Met` → move to the next section.
- `⚠️ Partial` / `❌ Not Met` → read the Recommended Next Step, ask the user
  a targeted follow-up (quote what's missing or weak), revise the section,
  and re-check. Loop until Met or explicitly bypassed.
- `N/A` → acceptable, move on (this happens for Constraints/Glossary when
  they don't apply).

**Ignore every other row's status while working through this phase** — rows
for sections you haven't written yet will correctly show `❌ Not Met`;
that's expected, not a failure.

**Phase 1 content gate:** rows #1–7 are all `✅ Met` or `N/A`.

**Phase 1 process gate:** once content is done, confirm directly with the
user — don't infer from silence:

- Row #8 — Was this goals section reviewed with the Key Allies listed above?
- Row #9 — Was it reviewed with the broader/design-review team?
- Row #10 — Was it reviewed with partner teams (if any are involved)?

For each "no," tell the user this review needs to happen before the doc is
ready for the next phase, per the design review process — but if they
explicitly want to proceed anyway, note the skip in the doc and continue.

The template's `⚠️ STOP HERE` marker is the natural checkpoint here — don't
remove it; it's there for the next human reader too.

### Phase 2 — Design Doc

For each Challenge named in Phase 1, ask for **at least two candidate
solutions** with pros/cons before asking for a recommendation — if the user
offers only one, push back once ("what's a second option you ruled out, and
why?") before accepting a single-solution section as their final answer.
Then ask for the Recommendation, tying the choice back to the stated
Goals/Constraints.

Continue through the remaining sections in order:

| # | Section | Checklist row |
| - | ------- | -------------- |
| 1 | Strategy (per challenge: 2+ solutions, recommendation) | #11, #12 |
| 2 | Common Considerations | — |
| 3 | Cost | — |
| 4 | API | — |
| 5 | Risks and Open Questions | — |
| 6 | Acknowledgements *(populate from the Key Allies table)* | — |

Gate each section the same way as Phase 1 (check its row, loop on
Partial/Not Met, N/A is fine). Rows #13–15 and #24 (appendix for rejected
options, punting implementation detail, page-length/reviewability, and
written record of why) aren't tied to a single section — check them once at
the end of Phase 2 against the whole draft, and if `Partial`/`Not Met`, ask
what to trim, move to an appendix, or add rationale for.

**Phase 2 content gate:** rows #11–15 and #24 are all `✅ Met` or `N/A`.

**Phase 2 process gate:** confirm directly:

- Row #16 — Was this draft run by Key Allies, with their feedback
  incorporated?
- Row #17 — Did Key Allies give buy-in that it's ready for a wider audience?
- Row #18 — Was it reviewed with partner teams (if any)?

Same bypass rule as Phase 1.

### Phase 3 — Implementation

Ask for, and write:

| # | Section | Checklist row |
| - | ------- | -------------- |
| 1 | Schedule (estimate + milestones) | — |
| 2 | Blockers (if any are already known) | #22 |
| 3 | Diagrams *(optional — ask if there's anything worth diagramming)* | — |

Gate the Blockers section like a content gate (loop on Partial/Not Met) —
it's checkable evidence just like Key Allies.

**Phase 3 process gate:** confirm directly:

- Row #19 — Has (or will) the org-wide/interested-parties review happen,
  framed as information-sharing rather than a decision-making gate?
- Row #20 — Has the feature been estimated (Story Sizing or equivalent)?
- Row #21 — Have the milestones/work-items been reviewed with the team
  doing the implementation?
- Row #23 — Are blocker follow-ups planned as small, targeted sessions
  rather than re-convening the full review audience?

Same bypass rule.

### Phase 4 — Finalize

1. Invoke `mario-design-reviewer` one last time on the finished file and
   print its full 24-row readiness matrix and rollup line to the user.
2. Confirm the file path and report it.
3. If, during the conversation, a Challenge surfaced that's big enough to
   need its own Implementation Design doc (5+ engineers, or spans both
   control and data plane — see checklist row #14), say so explicitly and
   suggest running `mario-design-creator` again scoped to that sub-problem
   — this is the process's own Phase 4 recursion, not a one-off suggestion.

---

## Gotchas

- **`mario-design-reviewer` always grades all 24 rows**, regardless of how
  much of the doc exists — expect rows for sections you haven't reached yet
  to show `❌ Not Met`. Only read the row(s) relevant to your current gate;
  don't treat the rest as a report card.
- **Resuming an existing file**: if the chosen path already has content,
  don't overwrite it blindly — read it first, run `mario-design-reviewer`
  against it to see which rows are already `Met`, and resume from the first
  non-`Met`/non-`N/A` row instead of restarting the interview from scratch.
- **Key Allies and Blockers are additions to the base template**, not in the
  original design doc template this was built from — they exist so rows #7
  and #22 are gradable as document content rather than permanently stuck on
  "trust me, I asked." Don't drop them thinking they're optional filler.
- **Never invent an answer for the user.** If they haven't told you their
  Goals, Non-Goals, or a second solution option, ask — don't draft
  plausible-sounding content and present it as theirs.
- **Bypass is explicit only.** Don't read enthusiasm, urgency, or a topic
  change as permission to skip a gate — the user has to actually say so,
  and the doc has to say so too (a visible note, not a silent omission).
- **This skill writes files** (unlike `mario-design-reviewer`, which is
  read-only) — confirm the file path before the first write, and don't
  write outside the path the user gave or confirmed.
