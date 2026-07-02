---
name: mario-prfaq-reviewer
description: >-
  Review a PR/FAQ document (Amazon Working Backwards format) against Thread's
  32-item PR/FAQ Review Checklist and return a readiness matrix — the original
  checklist plus a Status verdict and a Recommended Next Step for every row.
  Use whenever the user asks to review, grade, or check a PRFAQ, press
  release/FAQ doc, or Working Backwards doc — even if they say "review my
  PRFAQ", "check this against the checklist", "is this PRFAQ ready", or paste
  a PRFAQ and ask "what's missing". Accepts the PRFAQ as pasted text, a local
  file, or an external link (Notion, Google Doc, or generic URL).
compatibility: >-
  Uses references/checklist.md (bundled, cached checklist — no live Notion
  fetch). For link input, uses notion-fetch for Notion URLs or WebFetch for
  other URLs.
metadata:
  author: mario
  version: "1.0"
  category: document-review
---

# PR/FAQ Reviewer

Grade a PR/FAQ document against Thread's canonical 32-item PR/FAQ Review Checklist and hand back an actionable readiness matrix — not just a pass/fail, but exactly what to fix and where.

---

## The rule

The checklist in [references/checklist.md](references/checklist.md) is the company's rubric — **never reword, reorder, drop, or add rows to it.** Your only job is to append two columns of assessment. If Mario asks you to change the checklist itself, that's a different task — point him to updating the source Notion page and refreshing this cache (see Gotchas).

---

## Step 1: Get the PRFAQ

Accept whatever form the user gives you:
- **Pasted text** — use directly.
- **Local file** — read it.
- **External link** — use `notion-fetch` for a Notion URL, `WebFetch` for anything else (Google Doc export link, Confluence, plain webpage).

If the user references a PRFAQ but provides none of the above (no paste, no path, no link), ask for it before doing anything else — don't guess at content or invent a placeholder review.

---

## Step 2: Load the checklist

Read [references/checklist.md](references/checklist.md). It has 32 rows with columns **# | Best Practice | Examples | How to Use It | How It Helps | Source(s)**. Load it in full — don't summarize or sample it, every row gets evaluated.

---

## Step 3: Evaluate every row against the actual document

For each of the 32 rows, find the specific part of the PRFAQ that bears on that criterion. Ground every verdict in what the document actually says — quote or closely paraphrase it — rather than a generic impression. This is what turns a checklist into a real review instead of a rubber stamp.

Assign a **Status**:
- `✅ Met` — the PRFAQ clearly satisfies this practice.
- `⚠️ Partial` — attempted but weak, vague, or incomplete (e.g., a customer segment named but not narrow; benefits stated but not quantified).
- `❌ Not Met` — absent entirely.
- `N/A` — genuinely doesn't apply to this PRFAQ (e.g., row 20's competitive-alternatives FAQ for a purely internal tool with no market alternative). Use sparingly — most rows apply to most PRFAQs — and say why in the next-step column. `N/A` means *the criterion doesn't apply to this kind of product or launch* — it does not mean "the document didn't address it." A gap the document should have covered is `Not Met`, never `N/A`. Exception: a handful of rows (17, 26, 27, 28, 32) describe the *authoring/review process*, not the document's content — a finished PRFAQ can never provide evidence either way for these, so score them `N/A` by default rather than straining to force a Met/Not Met verdict.

If a criterion is satisfied in one section of the doc but not reinforced elsewhere (e.g., a number appears in the press release but isn't repeated in the FAQ), score on the best evidence found anywhere in the document — don't penalize for lack of repetition. If sections actively contradict each other, that's a `Partial` and the next step should say so.

Write a **Recommended Next Step**:
- For `Met` — a short confirming note (what specifically satisfies it), so the reader can spot-check without re-deriving the verdict.
- For `N/A` — one sentence on why it doesn't apply.
- For `Partial` / `Not Met` — a concrete, specific instruction tied to the actual document. Reference what's currently there (or missing) and what to change. Never write generic boilerplate like "add more detail" — say what detail, where, and why it's currently insufficient.

---

## Step 4: Render the readiness matrix

Output one markdown table, all 32 rows, in original order, with all six original columns intact plus the two new ones:

```
| # | Best Practice | Examples | How to Use It | How It Helps | Source(s) | Status | Recommended Next Step |
```

Before the table, add a one-line rollup so Mario can triage at a glance, e.g.:

```
**24/32 met · 5 partial · 2 not met · 1 N/A** — biggest gaps: #8 (no quantified benefits), #19 (TAM not sized), #23 (risks not surfaced).
```

Print the full table — never truncate to "top issues only" unless the user explicitly asks for a shortened view.

---

## Gotchas

- **The checklist is a cached snapshot**, not a live Notion fetch — it was captured from the source page and lives in `references/checklist.md`. If Mario has since edited the Notion checklist, this copy can drift out of date. If he mentions the checklist changed, refresh the file by re-fetching the Notion page rather than hand-editing rows.
- **Don't invent evidence.** If a section of the PRFAQ is genuinely ambiguous on a given criterion, mark it `⚠️ Partial` and say what's ambiguous — don't force a `Met` or `Not Met` verdict you can't back with a quote.
- **`N/A` is an escape hatch, not a shortcut.** Overusing it (especially for FAQ-structure rows like #15, #16) hides real gaps. Default to evaluating every row as `Met`/`Partial`/`Not Met` unless it truly cannot apply.
- **Long PRFAQs**: if the document is very long, still evaluate all 32 rows — don't skip rows because the doc is dense. Take the time to locate the relevant section for each.
- **This skill only reads and prints** — it never writes back to Notion or any file. If Mario later wants the matrix saved somewhere (a file, a new Notion page), that's a follow-up ask, not part of this flow.
