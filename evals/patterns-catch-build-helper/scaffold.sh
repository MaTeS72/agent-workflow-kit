#!/usr/bin/env bash
# A Flutter page, and a hook config whose patterns rule bans _buildX() helpers.
set -euo pipefail
mkdir -p .claude lib/pages
cat > .claude/agent-workflow.json <<'EOF'
{
  "patterns": [
    {
      "glob": "lib/**/*.dart",
      "regex": "Widget\\s+_build\\w*\\(",
      "message": "Project rule: extract a StatelessWidget instead of a Widget _buildX() helper method."
    }
  ]
}
EOF
cat > lib/pages/home_page.dart <<'EOF'
import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: Text('Recipes')));
  }
}
EOF
