# Refactoring Decisions

This document captures decisions made during the repository refactoring (June 2026) to align with the AgentSkills specification.

## Decision 1: Use CLAUDE.md as the primary authorship guide

### Decision
Create a comprehensive [CLAUDE.md](CLAUDE.md) that becomes Claude's primary reference for skill authorship. This file combines the AgentSkills specification with Mario's personal workflow.

### Why
- Claude reads CLAUDE.md (and not arbitrary other docs) when invoked in a project
- The existing AGENTS.md was partly workflow notes, partly spec guidance—blended
- Separating spec guidance (CLAUDE.md) from workflow notes (AGENTS.md) makes each document clearer
- Centralizing authorship guidance in one file ensures Claude refers to the same playbook every time

### How
- CLAUDE.md contains: template walkthrough, field reference, best practices, gotchas handling, troubleshooting
- AGENTS.md now focuses on Mario's workflow and lessons learned
- CONTRIBUTING.md provides quick-start steps for developers

### Trade-offs
- More documentation to maintain (3 docs instead of 1)
- **Benefit**: Each doc has a clear purpose and audience; less context-bloat for Claude

---

## Decision 2: Keep `disable-model-invocation` field for backward compatibility

### Decision
Did not remove the `disable-model-invocation` field from existing skills. Instead, we added spec-compliant fields alongside it.

### Why
- The existing skills work well and removing the field might break deployment
- The field is non-standard but harmless; clients ignore unknown fields
- Adding `metadata` and `compatibility` alongside it doesn't conflict
- Changing existing deployed skills risks disruption

### How
- Added `compatibility` and `metadata` to all skills
- Left `disable-model-invocation` untouched in existing skills
- New skills should use spec-compliant frontmatter only (see SKILL.template.md)

### Trade-offs
- Inconsistency between old and new skills (intentional)
- **Benefit**: Zero risk to deployed skills; smooth forward migration

---

## Decision 3: Update SKILL.template.md to match AgentSkills spec

### Decision
Replaced the minimal template with a comprehensive one showing spec-compliant frontmatter and recommended instruction structure.

### Why
- The old template was 6 lines: just frontmatter placeholders
- It didn't guide authors toward proven patterns (phases, gotchas, confirmation)
- New authors had to reverse-engineer structure from existing skills
- The spec recommends certain patterns; the template should encourage them

### How
- Template now includes:
  - Full frontmatter with all optional fields (with guidance on when to use each)
  - Recommended section structure (Overview, Confirmation, Instructions, Gotchas)
  - Example phases and decision points
- New skills generated via `make generate` inherit this structure

### Trade-offs
- Template is longer and more opinionated
- **Benefit**: Faster skill creation with better defaults; less iteration needed

---

## Decision 4: Add `compatibility` field to existing skills

### Decision
Added the `compatibility` field to all 4 existing skills to document their environment requirements.

### Why
- The AgentSkills spec includes `compatibility` as a standard way to declare requirements
- Users installing skills should know upfront if they need git, GitHub CLI, network access, etc.
- Example: `pump-to-obsidian` requires `gh` and GitHub MCP; `resume-review` has no external dependencies
- Declaring this upfront prevents "why doesn't this work?" moments

### How
- `code-review`: "Requires git and GitHub CLI (gh)"
- `dev-workflow`: "Requires git, test suite, type checker, linter"
- `pump-to-obsidian`: "Requires git, GitHub CLI (gh), GitHub MCP"
- `resume-review`: Left blank (no external requirements)

### Trade-offs
- Slightly more verbose frontmatter
- **Benefit**: Clear expectations for users; no surprises at runtime

---

## Decision 5: Add `metadata` field with standard keys

### Decision
Added a `metadata` section with `author`, `version`, and `category` to all skills.

### Why
- The spec supports `metadata` for extensibility
- Standard keys help with categorization and version tracking
- Provides a place for future tooling (e.g., skill marketplace filtering by category)
- Sets a pattern for future skills

### How
```yaml
metadata:
  author: mario
  version: "1.0"
  category: code-review  # or: development, hiring, knowledge-management
```

### Categories chosen
- `code-review`: code-review
- `dev-workflow`: development
- `pump-to-obsidian`: knowledge-management
- `resume-review`: hiring

### Trade-offs
- Slightly more frontmatter per skill
- **Benefit**: Future-proofs for categorization, versioning, and tool support

---

## Decision 6: Create CONTRIBUTING.md for developers

### Decision
Create a new [CONTRIBUTING.md](CONTRIBUTING.md) with quick-start steps for creating and testing skills.

### Why
- README.md is focused on installation; it doesn't explain how to *author* skills
- Developers should be able to go from zero to working skill in 5 minutes
- Having dedicated contribution guidance reduces barrier to entry
- Provides a reference for the Makefile commands and testing workflow

### How
- CONTRIBUTING.md includes:
  - Quick 5-step workflow (`make generate` → edit → validate → test → commit)
  - Pointers to CLAUDE.md for detailed guidance
  - Example commands for Claude Code and Claude app
  - Structure of the repo
  - Troubleshooting and help section

### Trade-offs
- More documentation (but focused and non-overlapping with CLAUDE.md)
- **Benefit**: Clear on-ramp for skill authors

---

## Decision 7: Refactor AGENTS.md from "how to build skills" to "lessons learned"

### Decision
Rewrote [AGENTS.md](AGENTS.md) to focus on Mario's personal workflow and best practices, removing spec guidance that now lives in CLAUDE.md.

### Why
- AGENTS.md was 44 lines of workflow mixed with spec guidance
- Now CLAUDE.md handles all spec and authorship guidance
- AGENTS.md can now be a shorter, more focused document on workflow and lessons
- Readers looking for "how to build a skill" get directed to CLAUDE.md once, then to AGENTS.md for deeper patterns

### How
- Removed: detailed frontmatter explanation, validation rules, archaic gotchas about YAML colons
- Kept: the 8-step workflow, best practices (prescriptive, defaults, coherence, etc.), project structure overview
- Added: clearer references to CLAUDE.md and CONTRIBUTING.md

### Result
- AGENTS.md is now ~160 lines of focused workflow and philosophy
- CLAUDE.md is ~400 lines of comprehensive authorship guide
- CONTRIBUTING.md is ~150 lines of quick-start for developers

---

## Decision 8: Did not restructure skills into references/scripts/assets

### Decision
Existing skills keep all instructions in SKILL.md. Did not refactor them into separate `references/`, `scripts/`, or `assets/` directories.

### Why
- The spec supports progressive disclosure: instructions go in SKILL.md, heavy reference material in separate files
- Current skills are reasonably sized and well-organized
- Refactoring would require moving content around and updating internal links
- The pattern is documented for *future* skills via CLAUDE.md

### How
- CLAUDE.md documents the pattern and when to use it
- Future skills that exceed 400 lines should use separate files
- Existing skills remain as-is (if it works, don't touch it)

### Trade-offs
- Existing skills don't use the full spec's progressive disclosure pattern
- **Benefit**: Zero disruption; pattern available for future skills; clear migration path

---

## Summary

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| CLAUDE.md as primary guide | Claude reads it; clearer purpose | More docs to maintain |
| Keep `disable-model-invocation` | Zero disruption to deployed skills | Inconsistency with spec |
| Update template | Better defaults for new skills | Template is more opinionated |
| Add `compatibility` | Clear requirements upfront | Slightly more frontmatter |
| Add `metadata` | Future-proofs for tooling | Slightly more frontmatter |
| Create CONTRIBUTING.md | Clearer on-ramp for authors | More documentation |
| Refactor AGENTS.md | Clearer focus (workflow, not spec) | Less all-in-one reference |
| Don't restructure skills | Zero disruption; simplicity | Older skills don't use full spec |

All decisions prioritize **zero disruption** to existing deployed skills while **enabling better practices** for future skills.
