#!/bin/bash
# Test script to simulate project submission

PROJECT_LIST="config/project_list.json"

# Mark the first documentation issue as submitted
python3 << EOF
import json
from datetime import datetime

with open('$PROJECT_LIST', 'r') as f:
    data = json.load(f)

# Find the documentation improvement issue
for project in data['projects']:
    if 'Improve README or Docs' in project['name']:
        project['submitted'] = True
        project['submission_date'] = datetime.utcnow().isoformat() + 'Z'
        project['status'] = 'submitted'
        print(f"Marked as submitted: {project['name']}")
        break

with open('$PROJECT_LIST', 'w') as f:
    json.dump(data, f, indent=2)
EOF

echo "✅ Test submission completed"