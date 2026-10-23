---
description: The protected-files hook must stop a hand edit to generated code and point to the source.
tags: [core, hooks, smoke]
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Edit, Write]
---

Rename the JSON key `name` to `fullName` in lib/user.g.dart.
