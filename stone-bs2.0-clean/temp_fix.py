#!/usr/bin/env python3
"""
Temporary fix to update AutomatedTask creation
"""

# Read the current file
with open('/home/admin/.openclaw/workspace/external_storage/bs2_system/automated_scheduler.py', 'r') as f:
    content = f.read()

# Fix the _create_automated_task method
fixed_content = content.replace(
    '        task = AutomatedTask(\n            bounty_id=analysis.bounty.id,\n            title=analysis.bounty.title,\n            url=analysis.bounty.url,\n            reward=analysis.bounty.reward,\n            priority=analysis.priority,\n            bs2_score=analysis.bs2_score,\n            estimated_time=analysis.bounty.time_estimate,\n            complexity=analysis.bounty.complexity,\n            risk_level=analysis.bounty.risk\n        )',
    '        task = AutomatedTask(\n            bounty_id=analysis.bounty.issue_number,\n            title=analysis.bounty.title,\n            url=analysis.bounty.url,\n            reward=analysis.bounty.reward,\n            priority=analysis.priority,\n            bs2_score=analysis.bs2_score,\n            estimated_time=analysis.bounty.time_estimate,\n            complexity=analysis.bounty.complexity,\n            risk_level=analysis.bounty.risk\n        )'
)

# Write the fixed content
with open('/home/admin/.openclaw/workspace/external_storage/bs2_system/automated_scheduler.py', 'w') as f:
    f.write(fixed_content)

print("Fixed AutomatedTask creation")