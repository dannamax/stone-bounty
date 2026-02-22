#!/bin/bash

# Update Stone Bounty strategy based on lessons learned

echo "🔄 Updating Stone Bounty Strategy..."

# Backup current files
cp stone-bounty/current-opportunities.json stone-bounty/current-opportunities.json.bak
cp MEMORY.md MEMORY.md.bak

# Update current opportunities with new strategy
mv stone-bounty/current-opportunities-updated.json stone-bounty/current-opportunities.json

# Update memory with new strategy
cat >> MEMORY.md << EOF

## Strategy Updates (2026-02-16)

### New Project Filtering Rules
- **BLACKLISTED**: rust-lang/rust, vuejs/vue, microsoft/vscode, and other large/complex projects
- **PREFERRED**: Small to medium projects (<50k stars) with responsive maintainers
- **FOCUS AREAS**: Documentation, simple bug fixes, tests, accessibility improvements

### PR Quality Improvements  
- Strict submodule protection to prevent accidental modifications
- Commit message validation (no issue numbers in commits)
- Require actual code changes (no placeholder files)
- Style compliance checking before submission

### Success Metrics Target
- Target success rate: 15% (currently at ~17% with 1/6)
- Focus on quality over quantity
- Prioritize projects like Rustchain that provide clear feedback

### Current Active Opportunities (Post-Optimization)
- Scottcjn/Rustchain #180: API documentation (15 RTC) - HIGH PRIORITY
- openclaw/openclaw #42: CLI docs improvement (25 USD) - MEDIUM PRIORITY  
- clawhub/clawhub #15: Skill template generator (20 USD) - MEDIUM PRIORITY

### Deprioritized Opportunities
- vuejs/vue PRs: Keep monitoring but no new submissions
- microsoft/vscode PRs: Keep monitoring but no new submissions
- All rust-lang/rust opportunities: COMPLETELY AVOID

EOF

echo "✅ Strategy update complete!"
echo "📊 New focus: Quality documentation PRs on responsive small/medium projects"
echo "🎯 Next target: Scottcjn/Rustchain #180 (API documentation)"