# <Design Title>

Use this template to keep design docs consistent and easy to review. This
file is meant to be copied per design; the guidance under each heading is
authoring instruction — replace it with real content, and delete any heading
that doesn't apply (say why in the doc, don't just drop it silently).

## Problem

Write a clear description of the problem this document addresses before
proposing any design. It's difficult to review a solution without a strong
understanding of the original problem. If this design tackles a sub-problem
of a larger problem, say so explicitly. The problem statement should make the
setting and purpose of the doc clear.

If this doc addresses multiple problems, enumerate them so each can be
addressed individually in the Strategy section.

## Challenges

Describe the limitations that guide this design — they'll drive your
decisions, so readers should know about them up front. Challenges can
include (but aren't limited to): limitations of downstream dependencies,
cost, scale, requirements that limit facets of the design, or other
constraints.

## Customer Experience

Describe how a customer (and their end users) will use the thing being
designed.

## Goals

Goals should focus on security, availability, customer experience,
scalability, performance, operations, cost, and testability. State each goal
as a testable statement of fact — not a proposed solution. Avoid tying
implementation details to goals.

#### Non-goals (Out of Scope)

Establish goals this design explicitly does not cover. This refines scope
and improves design discussions and reviews. Give each non-goal a
one-sentence rationale, and note whether it's a one-way door (costly to
reverse) or two-way door (easy to revisit later).

## Constraints

*(Include this section only if there are concrete numeric requirements —
otherwise delete it.)* List hard numeric bars the solution must clear (e.g.
latency, capacity, scale) in one place, separate from the narrative goals
above.

## Glossary

Enumerate and define the acronyms and system-specific components referenced
throughout this document. Include any terms your audience may not already
know.

## Key Allies

Name the people who'll review this design with you before it goes wide. Fill
in real names, not placeholders.

| Role | Person | Why they are here |
| --- | --- | --- |
| Senior Engineer | | First point of contact for design feedback |
| PM | | Helps you understand the customer experience |
| Subject Matter Expert (SME) | | Ensures the design is technically feasible and helps you understand the system |
| Partner Team POC: `<team>` | | Ensures the team is aware of the work |
| Syntactic / Writing Feedback | | Ensures the writing is clear and readable |
| Meeting Host | | Helps run effective review meetings; ideally someone not otherwise involved in the project |
| Network Partner *(if applicable)* | | Needed when the project affects shared network/routing behavior |

# ⚠️ STOP HERE and get a goals review of the above sections before proceeding. ⚠️

See the design-review-process reference bundled with the `mario-design-reviewer`
skill for best practices on how and when to review a design doc.

## Strategy

For each problem this doc addresses, build a section describing the
solution. Focus on the strategy — dive into implementation detail only where
it's critical to justifying the choice of direction. Include other solutions
you considered and ruled out, with pros/cons for each, and justify your
final choice.

### `<Problem/Question>`

#### Solution 1

`<solution description>`
`<Pros/Cons>`

#### Solution 2

`<solution description>`
`<Pros/Cons>`

#### Recommendation

Explain why you chose this solution given the requirements/goals/constraints
and the pros/cons above. Connecting the logic back to goals and requirements
makes it easier for the reader to follow your reasoning.

Consider a comparison matrix to illustrate the tradeoffs:

| Feature | Approach 1 | Approach 2 | Approach 3 |
| --- | --- | --- | --- |
| Time to Market (rank, low is better) | 1 | 2 | 3 |
| Availability (rank, low is better) | 3 | 2 | 1 |
| Performance (rank, low is better) | 2 | 2 | 1 |
| Capacity (rank, low is better) | 2 | 3 | 1 |
| Complexity (rank, low is better) | 3 | 2 | 1 |
| Maintainability (rank, low is better) | 1 | 2 | 3 |

## Common Considerations

Consider elaborating how this design handles:

1. What will operations look like? Do we have the right metrics?
2. Lifecycle of configured resources (create/update/delete):
   1. How does this design protect against dangling resources?
   2. How are failures handled?
3. How will migration be handled? Will the change be backwards compatible?
   1. What is the customer experience during migration?
4. What are the region/zone or stack build-out implications?
5. What and how many dependencies does this strategy take? What value do
   they bring?
6. What is the rollout/deployment strategy? How will you do this safely?
7. Will there need to be a backfill?
8. Can configuration be made asynchronous? Synchronous configuration —
   especially on dependent services — is often a source of customer and
   operational pain.
9. How are you health-checking this?
10. How are you detecting problems? What visibility do operators or
    stakeholders have?
11. How are actions audited and tracked?
12. How will this feature be deployed? Is it part of existing modules, or
    does it need new modules or pipelines?

## Cost

Describe any cost considerations of this design and include them in your
tradeoffs where relevant.

## API

Describe public and internal API changes explicitly, and get them reviewed
as early as possible — API churn is almost guaranteed if consensus isn't
built early on the structure. Example of an API update to include in a
high-level design:

```
<string name="IpAddressType" />
<enum target="IpAddressType">
  <enumValue value="IPV4" name="IPV4" />
  <enumValue value="IPV6" name="IPV6" /> <!-- New -->
  <enumValue value="dualstack" name="dualstack" /> <!-- New -->
</enum>
```

## Risks and Open Questions

Call out any risks or open questions that arose while developing this
design.

## Acknowledgements

Thank the reviewers who were involved. This recognizes their contributions
and gives future readers a reference for who was around for the design
discussions.

# Appendixes

## Schedule

List milestones and estimates for building this solution, once the design
is stable. Estimates may not be required for a design review unless they
impact design choices. If this is a higher-level design, account for greater
uncertainty and be clear about it — implementation-level detail belongs in a
separate Implementation Design.

## Blockers

Track blockers raised during review, each with a named owner — the person
who raised it or has the most at stake in resolving it.

| Blocker | Owner | Status |
| --- | --- | --- |
| | | |

## Diagrams

Diagrams are a useful way to visually present design problems and/or
solutions.

### Tools

Use whichever diagramming tool fits your organization's data-handling policy
for sensitive design content.

- https://app.diagrams.net/

# Example / reference design docs

Seen a design doc that inspired you or raised the bar? Link it here for the
next person.
