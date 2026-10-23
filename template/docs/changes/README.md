# Changes

Work in progress, one folder per change: `YYYY-MM-DD-<slug>/`.

| File | Written by | Holds |
| ---- | ---------- | ----- |
| `brief.md` | `/prep` | The user's decisions and the reason for each |
| `plan.md` | `/recipe` | Phases, tasks with files and tests, edge states, data safety |

Both carry a `Status:` line near the top; once `plan.md` exists, its status is
the change's status. `/cook` ticks tasks as they land and updates the status
after each phase.

Clean as you go: the merge request that ships a change's last phase deletes its
folder. Git history keeps the record, and this folder only ever holds live work.

Reviewers' notes go to `.tasting/`, which is git-ignored and deleted after each
tasting.
