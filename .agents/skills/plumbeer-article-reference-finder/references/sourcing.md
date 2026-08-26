# Sourcing rules by category

Applies during Phase 3 of the main skill. These rules exist to keep the
reference table trustworthy — a wrong or lazy match is worse than an honest
"not found."

## Named people

1. Search `<full name> wikipedia`.
2. If a Wikipedia page comes back, verify it's the *same* person using
   details already in the article: occupation/role, organization, era,
   nationality, or anything else the article states about them. A shared
   name is common — don't match on name alone.
3. If verification fails (wrong person, or ambiguous with no way to tell),
   search more narrowly, e.g. `<name> <organization> wikipedia` or
   `<name> <role>`.
4. If no Wikipedia page exists for this person, fall back in this order:
   - Official bio (company/institution "about" or "team" page)
   - A reputable news profile or interview
   - Do not fall back to social media profiles as the reference link.
5. Mark the entry "No credible source found" only after trying steps 1–4.

## Factual claims and statistics

1. If the article names its source ("a 2023 WHO report found..."), search
   for that exact source first — don't substitute a different one that makes
   a similar-sounding claim.
2. If the article doesn't name a source, search for the specific number or
   claim, preferring:
   - The original study, dataset, or official report (primary source)
   - A government or institutional statistics page
   - A reputable outlet's direct reporting on the primary source
   over: aggregator blogs, SEO content farms, or other unsourced
   restatements of the same figure.
3. If multiple sources report slightly different numbers, prefer the most
   recent and most authoritative one, and note the discrepancy in "How it
   matches" rather than silently picking one.

## Organizations, places, and named works

1. Wikipedia is usually sufficient and gives the reader the most context.
2. Use the official site instead when the article's mention is really about
   what the organization currently does/offers (e.g. a product claim) rather
   than general background — Wikipedia may be stale for that.

## General quality bar

- Every link must come back from an actual `WebSearch`/`WebFetch` result.
  Never construct a plausible-looking URL from memory.
- Prefer sources in the same language as the article when equally
  authoritative options exist in multiple languages.
- Two occurrences of the same person/claim in one article get one reference
  entry, reused across table rows — don't duplicate the numbered list.
