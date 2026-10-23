# Serving a change

`/cook` and `/rush` both end here. Follow the steps in order; nothing is
deleted, committed or pushed before step 4.

1. **Final check.** Run the format check, lint and test commands from the "Key commands" table in AGENTS.md. Stop if anything is red.
2. **Docs.** Update every durable doc the change made false: the ones the recipe listed, or for a rush, any the fix touches.
3. **Status** (changes with a folder only). Rewrite the `Status:` line in `docs/changes/<folder>/plan.md`, for example `phase 1 of 2 in review (merge request 42); phase 2 next`. On the last phase, the folder will be removed in the commit below; don't delete it yet.
4. **Ask.** Show the diff summary and ask with **AskUserQuestion**:
   1. **Commit, push and open a merge request**
   2. **Commit only**
   3. **Leave everything uncommitted**

   If the user leaves it uncommitted, stop here and say what's left: the commit, and on the last phase, deleting the change folder in that commit.
5. **Commit.**
   - **First phase:** include the change folder (`brief.md`, `plan.md`), so the decisions live in git history from the start.
   - **Last phase:** remove the change folder in the same commit (`git rm -r docs/changes/<folder>`). Clean as you go.
   - Message: conventional (`<type>: <what changed>`); a rush uses `fix:` and names the symptom.
6. **Merge request** (only when chosen). Push the branch and open the request with the CLI that matches `git remote get-url origin`: `glab mr create` for GitLab, `gh pr create` for GitHub (a pull request there). Fill the description from the [template](merge-request.md), including open should-fix findings and the nits from the tasting notes. Without the CLI, print the description for the user to paste.
7. **Clean up.** Delete `docs/changes/.tasting/`; its findings now live in the description.
