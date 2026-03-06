#!/bin/bash
#
# BS2.0 Skills Integration Script
# Integrates superpowers and planning-with-files skills into BS2.0 system
#

set -e

BS2_DIR="/home/admin/.openclaw/workspace/stone-bs2.0"
SKILLS_DIR="/home/admin/.openclaw/workspace/skills"

echo "🚀 Starting BS2.0 Skills Integration..."

# Step 1: Create planning directory structure
echo "📁 Creating planning directory structure..."
mkdir -p "$BS2_DIR/docs/plans"
mkdir -p "$BS2_DIR/planning"

# Step 2: Copy skill templates to BS2.0
echo "📋 Copying skill templates..."
cp "$SKILLS_DIR/planning-with-files/templates/task_plan.md" "$BS2_DIR/planning/" 2>/dev/null || true
cp "$SKILLS_DIR/planning-with-files/templates/findings.md" "$BS2_DIR/planning/" 2>/dev/null || true
cp "$SKILLS_DIR/planning-with-files/templates/progress.md" "$BS2_DIR/planning/" 2>/dev/null || true

# Step 3: Create skills configuration
echo "⚙️  Creating skills configuration..."
cat > "$BS2_DIR/config/skills_config.json" << 'EOF'
{
  "superpowers": {
    "enabled": true,
    "workflow_mode": "subagent_driven",
    "require_design_approval": true,
    "tdd_enabled": true
  },
  "planning_with_files": {
    "enabled": true,
    "auto_create_planning_files": true,
    "session_recovery_enabled": true,
    "error_logging_enabled": true
  },
  "integration_points": {
    "bounty_analysis": ["planning_with_files"],
    "pr_generation": ["superpowers", "planning_with_files"],
    "error_handling": ["superpowers"]
  }
}
EOF

# Step 4: Update main BS2.0 script to support skills
echo "🔧 Updating BS2.0 main script..."
if ! grep -q "skills" "$BS2_DIR/bs2.sh"; then
    sed -i '/print_success() {/i\
print_info_skills() {\
    echo -e "${BLUE}🧠 Skills Integration: superpowers + planning-with-files${NC}"\
}' "$BS2_DIR/bs2.sh"
    
    # Add skills info to help
    sed -i '/For more information, see:/i\
    print_info_skills' "$BS2_DIR/bs2.sh"
fi

# Step 5: Create helper functions
echo "🛠️  Creating helper functions..."
cat > "$BS2_DIR/scripts/skills_helpers.py" << 'EOF'
"""
Helper functions for integrating superpowers and planning-with-files skills
into BS2.0 system.
"""

import os
import json
from datetime import datetime
from pathlib import Path

class BSSkillsIntegrator:
    """Integrates skills into BS2.0 workflow"""
    
    def __init__(self, bs2_dir: str):
        self.bs2_dir = Path(bs2_dir)
        self.planning_dir = self.bs2_dir / "planning"
        self.config_file = self.bs2_dir / "config" / "skills_config.json"
        self.load_config()
    
    def load_config(self):
        """Load skills configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
    
    def create_planning_files(self, task_name: str, issue_url: str = ""):
        """Create planning files for a new task"""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        # Create task_plan.md
        task_plan_content = f"""# BS2.0 Task Plan: {task_name}

## Task Information
- **Issue URL**: {issue_url}
- **Created**: {datetime.now().isoformat()}
- **Status**: initialized

## Phases
| Phase | Status | Description |
|-------|--------|-------------|
| Bounty Analysis | pending | Analyze bounty requirements and constraints |
| Solution Design | pending | Design solution using superpowers workflow |
| Implementation | pending | Execute implementation with TDD |
| PR Creation | pending | Create and submit Pull Request |
| Verification | pending | Verify PR meets all requirements |

## Progress Tracking
- [ ] Task initialized
- [ ] Analysis complete  
- [ ] Design approved
- [ ] Implementation complete
- [ ] PR created
- [ ] Task completed

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
"""
        
        with open(self.planning_dir / "task_plan.md", 'w') as f:
            f.write(task_plan_content)
        
        # Create findings.md
        findings_content = f"""# Findings for {task_name}

## Research Results
- **Issue Analysis**: 
- **Technical Requirements**: 
- **Dependencies**: 
- **Constraints**: 

## Discoveries
"""
        with open(self.planning_dir / "findings.md", 'w') as f:
            f.write(findings_content)
        
        # Create progress.md  
        progress_content = f"""# Progress Log for {task_name}

## Session Start
{datetime.now().isoformat()} - Task started

## Activities
"""
        with open(self.planning_dir / "progress.md", 'w') as f:
            f.write(progress_content)
    
    def update_task_plan_status(self, phase: str, status: str = "complete"):
        """Update task plan phase status"""
        task_plan_file = self.planning_dir / "task_plan.md"
        if task_plan_file.exists():
            with open(task_plan_file, 'r') as f:
                content = f.read()
            
            # Update phase status in markdown table
            updated_content = content.replace(
                f"| {phase} | pending |",
                f"| {phase} | {status} |"
            )
            
            with open(task_plan_file, 'w') as f:
                f.write(updated_content)
    
    def log_error(self, error: str, attempt: int, resolution: str = ""):
        """Log error to task plan"""
        task_plan_file = self.planning_dir / "task_plan.md"
        if task_plan_file.exists():
            with open(task_plan_file, 'r') as f:
                content = f.read()
            
            # Find errors section and append
            if "## Errors Encountered" in content:
                error_line = f"| {error} | {attempt} | {resolution} |\n"
                content = content.replace(
                    "## Errors Encountered\n| Error | Attempt | Resolution |\n|-------|---------|------------|",
                    f"## Errors Encountered\n| Error | Attempt | Resolution |\n|-------|---------|------------|\n{error_line}"
                )
            
            with open(task_plan_file, 'w') as f:
                f.write(content)

# Usage example:
# integrator = BSSkillsIntegrator("/path/to/bs2")
# integrator.create_planning_files("Fix issue #123", "https://github.com/.../issues/123")
EOF

echo "✅ BS2.0 Skills Integration Complete!"

echo ""
echo "📚 Next Steps:"
echo "1. Review the created files in $BS2_DIR/planning/"
echo "2. Test integration with: cd $BS2_DIR && ./bs2.sh test"
echo "3. Use enhanced workflow for new bounties"
echo ""
echo "💡 The integrated system now provides:"
echo "- Persistent planning with planning-with-files"
echo "- Structured development workflow with superpowers"  
echo "- Better error handling and debugging"
echo "- Improved code quality through TDD"