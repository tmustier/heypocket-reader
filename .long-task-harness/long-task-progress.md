# heypocket-reader - Progress Log

## Project Overview

**Started**: 2025-12-31
**Status**: In Progress
**Repository**: [Add git remote URL]

### Project Goals

[Describe what you're building and why]

### Key Decisions

[Document important architectural or design decisions - reference session numbers]

---

## Current State

**Last Updated**: 2025-12-31

### What's Working
- [List functional features]

### What's Not Working
- [List known issues]

### Blocked On
- [List blockers]

---

## Session Log

### Session 1 | 2025-12-31 | Commits: [first..last]

#### Metadata
- **Features**: setup-001 (started)
- **Files Changed**: 
  - `package.json` (+15/-0) - initial dependencies
  - `src/index.ts` (+45/-0) - entry point
- **Commit Summary**: `init: project scaffold`, `feat: add base config`

#### Goal
Project initialization and setup

#### Accomplished
- [x] Initialized long-task-harness structure
- [x] Created initial feature list
- [ ] [Incomplete task carried forward]

#### Decisions
- **[D1]** Chose TypeScript over JavaScript for type safety
- **[D2]** Using pnpm over npm for faster installs

#### Context & Learnings
[What you learned, gotchas encountered, why things were done a certain way]

#### Next Steps
1. [First priority] → likely affects: feature-001
2. [Second priority]

---

<!--
=============================================================================
SESSION TEMPLATE - Copy below this line for new sessions
=============================================================================

### Session N | YYYY-MM-DD | Commits: abc123..def456

#### Metadata
- **Features**: feature-id (started|progressed|completed|blocked)
- **Files Changed**: 
  - `path/to/file.ts` (+lines/-lines) - brief description
- **Commit Summary**: `type: message`, `type: message`

#### Goal
[One-liner: what you're trying to accomplish this session]

#### Accomplished
- [x] Completed task
- [ ] Incomplete task (carried forward)

#### Decisions
- **[DN]** Decision made and rationale (reference in features.json)

#### Context & Learnings
[What you learned, gotchas, context future sessions need to know.
Focus on WHAT and WHY, not the struggle/errors along the way.]

#### Next Steps
1. [Priority 1] → likely affects: feature-id
2. [Priority 2]

=============================================================================
GUIDELINES FOR GOOD SESSION ENTRIES
=============================================================================

1. METADATA is for machines (subagent lookup)
   - Always list features touched with status
   - Always list files with change magnitude
   - Always include commit range or hashes

2. DECISIONS are for continuity
   - Number them [D1], [D2] so they can be referenced
   - Copy key decisions to features.json history
   - Include rationale, not just the choice

3. CONTEXT is for future you/agents
   - Capture the WHY behind non-obvious choices
   - Note gotchas and edge cases discovered
   - Omit error-correction loops - just document resolution

4. COMMIT SUMMARY style
   - Use conventional commits: feat|fix|refactor|test|docs|chore
   - Keep to one-liners that scan quickly

5. Keep sessions BOUNDED
   - One session = one work period (not one feature)
   - If session runs long, split into multiple entries
   - Target: scannable in <30 seconds

-->
