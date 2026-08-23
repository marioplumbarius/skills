---
name: plumbeer-skill-backwards
description: >-
  Analyze the current Claude session, apply the STAR framework (Situation,
  Task, Action, Result) to reconstruct the thought process from ideation to
  resolution, and write a structured markdown retrospective to a local file.
  Use when the user says "retrospective", "document this session",
  "skill backwards", "write up what we did", or wants a structured record of
  a problem-solving session.
metadata:
  author: plumbeer
  version: "1.0"
  category: knowledge-management
---

# Skill Backwards

Turn a Claude session into a structured retrospective using the STAR framework.
Draft first, get approval, then write to a local markdown file.

```
- [ ] Phase 1: Gather & scope
- [ ] Phase 2: STAR analysis
- [ ] Phase 3: Draft + present plan (GATE: approval)
- [ ] Phase 4: Write file + report
```

## Phase 1 — Gather & Scope

Read this session's full conversation and tool history. Do not invent content —
only work from what actually happened.

Extract:
- **The inciting problem** — what prompted the session; what was broken, missing, or unknown at the start
- **The goal** — stated or inferred objective
- **The moves** — key decisions, rejected alternatives, pivots, and the reasoning behind each
- **The outcome** — what is now true, including any unresolved threads

If the session covered multiple unrelated problems, ask the user which thread to
scope to before proceeding. One retrospective per problem thread.

## Phase 2 — STAR Analysis

Map the gathered material to the four STAR sections:

**Situation** — the context *before* the work began. What was the state of the world
that made this session necessary? Ground it in real impact: what was failing, blocked,
or unknown. One or two sentences.

**Task** — the concrete goal this session set out to accomplish. If the user stated it
explicitly, use that. If it was implicit, name it clearly. One sentence.

**Action** — this is the hardest section and the most important. Write a *reasoning
narrative*, not a transcript. The question is: why was each step taken? Capture the
thought process: what was considered first and why, what was tried and discarded, what
pivots happened and what caused them, and why the final approach was chosen over
alternatives. This should read like a structured chain of reasoning, not a timeline of
tool calls.

**Result** — what is now true that wasn't before. Include partial or tentative outcomes
honestly. If the session ended with open questions, name them — don't round up to a
conclusion that wasn't reached.

## Phase 3 — Draft + present plan

Build the full document in memory using the template below. Then show the user:

1. **Proposed filename:** `YYYY-MM-DD-<kebab-slug>-retrospective.md` using today's date
   and a short slug from the session topic.
2. **Proposed path:** current working directory, unless the user specified a path.
3. **Full document preview** — show everything so the user can read and edit before it
   lands on disk.

Use this template:

```markdown
---
title: <human-readable title>
date: YYYY-MM-DD
source: <claude-code | cowork | chat>
tags: [retrospective, star-framework, <topic-tags>]
---

# <title>

## Situation
<What was the context before this session started? What was broken, unknown, or needed?>

## Task
<What was the concrete goal — stated or implied — that this session set out to accomplish?>

## Action
<Narrative of the thought process: what was considered, why each direction was chosen,
what was ruled out and why. Not a transcript — a structured reasoning trace.>

## Result
<What is now true that wasn't before? Include partial outcomes and open threads honestly.>

## Open threads
- [ ] <anything unresolved>
```

Drop **Open threads** if there are none. Drop any other section only if it genuinely
has nothing to say — don't ship empty headers.

**GATE:** Present the draft and wait for explicit approval. If the user requests
changes, revise and re-present. Do not write the file until they approve.

## Phase 4 — Write file + report

Write the approved content to the proposed path. If a file with that exact name already
exists, append `-2` (or `-3`, etc.) rather than overwriting.

Report:
- Full path of the file written
- Word count of the Action section (a proxy for reasoning depth — aim for >80 words)

## Gotchas

- **Action depth.** The Action section must explain *why*, not *what*. "We ran git diff
  then edited the file" is a transcript. "We started with git diff to isolate scope
  before touching any code, because the symptom could have been in three places" is a
  reasoning trace. Rewrite until it reads like the second.
- **Ephemeral environments.** In remote containers the file may not persist after the
  session ends. Mention this in the Phase 3 presentation so the user can copy the draft
  from the gate if they need it immediately.
- **Long sessions.** If the session has many unrelated threads, scope to one before
  drafting — ask the user which. A focused retrospective beats an exhaustive summary.
- **No secrets.** If the Action section references code or commands, strip API keys,
  tokens, and credentials before writing.
- **Honesty over polish.** If a decision was wrong, a test failed, or the outcome was
  partial, say so. Don't retrospectively narrate the session as if every move was
  deliberate and correct.
