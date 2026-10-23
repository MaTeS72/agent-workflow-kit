---
type: feat | fix | refactor | chore
created: YYYY-MM-DD
---

# <type>: <description>

> **Status:** recipe written — no phase cooked yet. /cook ticks tasks as they
> land and rewrites this line after each phase; the merge request that ships
> the last phase deletes this folder.

## Why

<The problem, who has it, and what done looks like. Link the brief if there is one.>

## Approach

<Components and data flow, and the existing patterns followed, each with a
`file:line` example.>

## Phase 1 — <name>

Ships on its own.

- [ ] **<Task>** — `<path>` (new | change). Tests: `<path>` — <what they prove>.

Done when:

- [ ] <Observable outcome.>

*Add a Phase 2 only when one merge request would be too big, or would mix a
one-way step with other work.*

## Edge states

- [ ] Empty: <behaviour>
- [ ] Loading: <behaviour>
- [ ] Error: <behaviour>
- [ ] Offline: <behaviour>
- [ ] Permission denied: <behaviour>
- [ ] First run: <behaviour>

## Data safety

- **Stored or synced shapes changed:** <list, or none>. Old data still loads because <reason>.
- **Destructive writes:** <list, or none>. Guarded by <confirmation | soft delete | backup | dry run>.
- **Sign-out and account switch:** <what must reset, or nothing new>.

## Docs to update

- <Durable docs this change makes stale, or none.>

## Risks and rollback

- <Risk> — <mitigation>. Rollback: <how to undo each phase, especially a one-way step>.
