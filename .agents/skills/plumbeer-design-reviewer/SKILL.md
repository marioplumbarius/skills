---
name: plumbeer-design-reviewer
description: >-
  Review a design doc against a 24-item Design Doc Review Checklist derived
  from references/design-review-process.md, and return a readiness matrix —
  the original checklist plus a Status verdict and a Recommended Next Step
  for every row. Use whenever the user asks to review, grade, or check a
  design doc, high-level design, or goals doc — even if they say "review my
  design doc", "check this against our design review process", "is this
  design ready for org-wide review", or paste a design doc and ask "what's
  missing". Accepts the design doc as pasted text, a local file, or an
  external link (Notion, Google Doc, or generic URL).
compatibility: >-
  Uses references/checklist.md, the bundled canonical checklist derived from
  references/design-review-process.md. For link input, uses notion-fetch for
  Notion URLs or WebFetch for other URLs.
metadata:
  author: plumbeer
  version: "1.0"
  category: document-review
---

# Design Doc Reviewer

Grade a design doc against a canonical 24-item Design Doc Review Checklist and hand back an actionable readiness matrix — not just a pass/fail, but exactly what to fix and where.

---

## The rule

The checklist in [references/checklist.md](references/checklist.md) is the canonical rubric — **never reword, reorder, drop, or add rows to it during a review.** Your only job is to append two columns of assessment. If the underlying [references/design-review-process.md](references/design-review-process.md) changes and the checklist needs to follow, that's a separate, deliberate task: edit `references/checklist.md` directly, the same way you'd edit any other canonical document — don't silently regenerate it mid-review.

---

## Step 1: Get the design doc

Accept whatever form the user gives you:
- **Pasted text** — use directly.
- **Local file** — read it.
- **External link** — use `notion-fetch` for a Notion URL, `WebFetch` for anything else (Google Doc export link, Confluence, plain webpage).

If the user references a design doc but provides none of the above (no paste, no path, no link), ask for it before doing anything else — don't guess at content or invent a placeholder review.

---

## Step 2: Load the checklist

Read [references/checklist.md](references/checklist.md). It has 24 rows with columns **# | Best Practice | Examples | How to Use It | How It Helps | Source(s)**. Load it in full — don't summarize or sample it, every row gets evaluated.

---

## Step 3: Evaluate every row against the actual document

For each of the 24 rows, find the specific part of the design doc that bears on that criterion. Ground every verdict in what the document actually says — quote or closely paraphrase it — rather than a generic impression.

Assign a **Status**:
- `✅ Met` — the doc clearly satisfies this practice.
- `⚠️ Partial` — attempted but weak, vague, or incomplete (e.g., a non-goal stated but no rationale given; solutions presented but only one is fully fleshed out).
- `❌ Not Met` — absent entirely, and the doc is the kind of doc this criterion should apply to.
- `N/A` — genuinely doesn't apply. Use sparingly and say why in the next-step column. A gap the doc should have covered is `Not Met`, never `N/A`.

**Rows 8–10 and 16–23 describe review *process* (meetings held, allies consulted, blockers assigned) rather than the document's own content.** A standalone design doc usually can't prove these either way unless it includes its own review history (a changelog, revision log, or an explicit "reviewed by" section) — score these `N/A` by default, and only mark `Met`/`Partial`/`Not Met` when the doc itself documents that history, or the user explicitly tells you the review status. Don't infer a review happened just because the doc looks polished. Rows 1–7, 11–15, and 24 are about the document's own content and should be evaluated normally against what's actually written.

If a criterion is satisfied in one section of the doc but not reinforced elsewhere, score on the best evidence found anywhere in the document — don't penalize for lack of repetition. If sections actively contradict each other, that's a `Partial` and the next step should say so.

Write a **Recommended Next Step**:
- For `Met` — a short confirming note (what specifically satisfies it), so the reader can spot-check without re-deriving the verdict.
- For `N/A` — one sentence on why it doesn't apply (for process rows, usually: "no review history documented in the doc").
- For `Partial` / `Not Met` — a concrete, specific instruction tied to the actual document. Reference what's currently there (or missing) and what to change. Never write generic boilerplate like "add more detail" — say what detail, where, and why it's currently insufficient.

---

## Step 4: Render the readiness matrix

Output one markdown table, all 24 rows, in original order, with all six original columns intact plus the two new ones:

```
| # | Best Practice | Examples | How to Use It | How It Helps | Source(s) | Status | Recommended Next Step |
```

Before the table, add a one-line rollup so the reader can triage at a glance, e.g.:

```
**14/24 met · 3 partial · 1 not met · 6 N/A** — biggest gaps: #4 (non-goals lack rationale), #11 (only one solution presented for the routing challenge), #6 (no Challenges section).
```

Print the full table — never truncate to "top issues only" unless the user explicitly asks for a shortened view.

---

## Gotchas

- **`references/checklist.md` is the canonical checklist**, derived once from [references/design-review-process.md](references/design-review-process.md) — there's no live sync between the two at review time. If the process doc changes, update the checklist deliberately as its own edit.
- **Don't invent evidence.** If a section of the design doc is genuinely ambiguous on a given criterion, mark it `⚠️ Partial` and say what's ambiguous — don't force a `Met` or `Not Met` verdict you can't back with a quote.
- **`N/A` is an escape hatch, not a shortcut** — but rows 8–10 and 16–23 are the deliberate exception, since a document can rarely prove its own review process happened. Don't extend that same generosity to rows 1–7, 11–15, or 24, which are about content the doc should actually contain.
- **Long design docs**: still evaluate all 24 rows — don't skip rows because the doc is dense or the relevant section is buried in an appendix.
- **This skill only reads and prints** — it never writes back to Notion or any file. If the user later wants the matrix saved somewhere, that's a follow-up ask, not part of this flow.
