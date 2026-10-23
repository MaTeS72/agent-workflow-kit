## What

<One or two sentences: what this change does for the user.>

Cooks phase <n> of `docs/changes/<folder>/plan.md` (<"last phase: change folder deleted" | "phases n+1… still to cook">).

## Why

<The problem, linked to the issue or the brief.>

## How to verify

- <Command, screen or request that shows it working.>
- <An edge state worth checking by hand: empty, offline, error.>

## Tasting

- Tasted by the rules, test, data-safety, docs-drift and pre-merge reviewers; blockers fixed.
- Open should-fix findings: <list, or "none">.
- Nits for later: <list, or "none">.

## Checklist

- [ ] Format, lint and tests pass
- [ ] Tests prove the happy path, the failure paths and the edge states
- [ ] Stored data written by the previous version still loads
- [ ] Durable docs updated in this change
- [ ] Change folder status updated, or the folder deleted
