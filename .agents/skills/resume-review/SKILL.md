---
name: resume-review
description: >-
  Use this skill to review resumes for senior, staff, or principal software
  engineering roles. Apply it when given a resume and a job description, even
  if the user doesn't explicitly say "resume review." Produces structured,
  section-by-section feedback using Amazon Leadership Principles (signal
  detection + per-LP scoring) and the SMART framework across the full resume.
  Outputs a final phone screen / reject recommendation. Requires both a resume
  and a job description to proceed.
---

# Resume Review — Senior/Staff/Principal SWE

First-pass screening tool for hiring managers. Requires both a **resume** and a
**job description (JD)**. If either is missing, ask for it before proceeding.

---

## Review workflow

Work through each phase in order. Do not skip phases.

```
- [ ] Phase 1: Parse inputs
- [ ] Phase 2: SMART audit (full resume)
- [ ] Phase 3: LP signal detection
- [ ] Phase 4: LP scoring
- [ ] Phase 5: Section-by-section feedback
- [ ] Phase 6: Verdict
```

---

## Phase 1 — Parse inputs

Extract and summarize:

- **Role**: title, level, team/domain from JD
- **Must-haves**: hard requirements stated in JD (years of experience, specific
  tech, domain knowledge)
- **LP emphasis**: note any LPs the JD language leans into (e.g., "move fast" →
  Bias for Action; "raise the bar" → Hire and Develop the Best)
- **Candidate snapshot**: current role, years of experience, tech stack,
  domains covered

Flag immediately if the candidate is a **clear miss** on any must-have (e.g.,
JD requires 8+ years, candidate has 3). Still complete the review but note the
hard blocker upfront.

---

## Phase 2 — SMART audit

Apply the SMART framework across the entire resume. For each section evaluate:

| Section | What to check |
|---|---|
| Summary / objective | Specific to this type of role? Relevant claims? Not generic boilerplate? |
| Experience bullets | Each bullet: Specific scope + Measurable outcome + Relevant to JD + Time context |
| Skills | Credible and organized by category, not a keyword dump |
| Projects | Clear scope, impact, and time range stated |

**Flag** any bullet or claim that is vague, unmeasured, or irrelevant to the
JD. For each flagged item, provide a concrete rewrite example.

```
Weak:  "Improved system performance."
Fixed: "Reduced API p99 latency from 850ms to 120ms by introducing a
        Redis caching layer, handling 3× peak traffic without additional
        infrastructure (Q3 2023)."
```

---

## Phase 3 — LP signal detection

Scan the resume for evidence of each of Amazon's 16 Leadership Principles.
Mark each as:

- **Strong** — explicit, quantified evidence
- **Weak** — implied or vague reference
- **Absent** — no evidence found

The 16 LPs:

1. Customer Obsession
2. Ownership
3. Invent and Simplify
4. Are Right, A Lot
5. Learn and Be Curious
6. Hire and Develop the Best
7. Insist on the Highest Standards
8. Think Big
9. Bias for Action
10. Frugality
11. Earn Trust
12. Dive Deep
13. Have Backbone; Disagree and Commit
14. Deliver Results
15. Strive to be Earth's Best Employer
16. Success and Scale Bring Broad Responsibility

Cross-reference with the LP emphasis noted in Phase 1. LPs the JD prioritizes
carry more weight.

---

## Phase 4 — LP scoring

Score each LP from 0–3:

| Score | Meaning |
|---|---|
| 0 | Absent — no evidence |
| 1 | Weak — implied, no specifics |
| 2 | Moderate — clear example, limited scope or impact |
| 3 | Strong — explicit, quantified, significant scope |

Compute an **overall LP signal score**: sum / (3 × number of JD-prioritized LPs).
Express as a percentage. Flag any JD-prioritized LP scoring 0 or 1.

---

## Phase 5 — Section-by-section feedback

Structure feedback as follows for each resume section:

```
### [Section name]

**Strengths**: ...
**Gaps**: ...
**Suggested rewrites** (if any):
  - Original: "..."
    Revised:  "..."
```

Sections to cover (skip if not present in resume):

- Contact / header
- Summary / objective
- Experience (one subsection per role)
- Skills
- Education
- Projects / open source
- Publications / patents (if present)

---

## Phase 6 — Verdict

Output a final summary block:

```
## Screening verdict

**Recommendation**: [Advance to phone screen | Reject]

**Overall LP signal**: X% (Y / Z JD-prioritized LPs with strong signal)

**Key strengths**:
- ...

**Key concerns**:
- ...

**Hard blockers** (if any):
- ...

**Suggested phone screen focus** (if advancing):
- LP gaps to probe: ...
- Technical areas to validate: ...
```

### Decision rules

- **Advance** if: no hard blockers AND overall LP signal ≥ 50% AND at least one
  JD-prioritized LP scores 3
- **Reject** if: any hard blocker OR overall LP signal < 30%
- **Judgment call** (state explicitly) if: 30–49% LP signal, no hard blockers —
  weigh domain fit and seniority trajectory before deciding

---

## Gotchas

- **Don't penalize format over substance.** A plain-text resume with strong LP
  signal beats a beautifully formatted one with vague bullets.
- **Titles lie, bullets don't.** A "Senior Engineer" title at a small startup
  may outperform a "Staff Engineer" title at a large company — judge by evidence.
- **Recency matters.** Weight the last 3 years of experience more heavily than
  older roles.
- **Absence ≠ failure.** Not every LP needs to be present. Focus on LPs the JD
  emphasizes.
- **SMART rewrites are suggestions, not requirements.** They help the candidate
  if feedback is shared; they also help the reviewer assess true impact vs.
  poor articulation.
