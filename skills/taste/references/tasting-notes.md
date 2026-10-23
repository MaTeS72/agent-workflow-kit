# Tasting-notes contract

`/taste`, `/cook` and `/rush` append this contract to every taster's prompt.
Full notes go to a file; the caller sees a short summary and opens a note only
to fix what it describes.

## Scope

Taste only the files listed in your prompt. Open other files only to check the
callers of a changed API, or the pattern a change claims to follow.

## Evidence

- Give `path:line` for every finding, and read the code before you cite it.
- "This might break" needs the input or sequence that breaks it.
- Report; don't fix. The only file you write is your note.

## Labels

| Label | Meaning | Examples |
| ----- | ------- | -------- |
| **blocker** | Can't merge like this | Bug, data loss, security hole, red build or lint, new logic without tests, a broken absolute rule from AGENTS.md |
| **should-fix** | Fix it in this change unless the user decides otherwise | Convention slip, weak test, misleading name, a durable doc the change made stale |
| **nit** | Take it or leave it | Readability, a smaller equivalent, a follow-up idea |

## Your note

Write it to `docs/changes/.tasting/<agent-name>.md` (create the folder if
needed):

```markdown
# <agent-name>

Verdict: <merge as is | merge after fixes | rethink the approach> — <one sentence why>

## Blockers

- `path:line` — <problem>. Because: <consequence>. Fix: <concrete change>.

## Should-fix

## Nits
```

## What you return

Return only this, at most 12 lines:

```markdown
**<agent-name>** — <verdict> — docs/changes/.tasting/<agent-name>.md
blockers <n> · should-fix <n> · nits <n>
- blocker `path:line` — <one line>
- should-fix `path:line` — <one line>
```
