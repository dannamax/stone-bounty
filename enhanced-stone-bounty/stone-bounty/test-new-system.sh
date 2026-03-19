#!/bin/bash

echo "🧪 Testing New Stone Bounty System..."

# Test 1: Project filtering
echo "Test 1: Project filtering"
cd /home/admin/.openclaw/workspace/stone-bounty
if python3 bounty-evaluator.py; then
    echo "✅ Project filtering test passed"
else
    echo "❌ Project filtering test failed"
fi

# Test 2: Opportunity discovery  
echo "Test 2: Opportunity discovery"
if python3 opportunity-discoverer.py; then
    echo "✅ Opportunity discovery test passed"
else
    echo "❌ Opportunity discovery test failed"
fi

# Test 3: Configuration loading
echo "Test 3: Configuration loading"
if [[ -f "config.json" && -f "project-filter.json" ]]; then
    echo "✅ Configuration files loaded"
else
    echo "❌ Configuration files missing"
fi

# Test 4: Memory update
echo "Test 4: Memory update"
if grep -q "策略更新 (2026-02-16)" ../MEMORY.md; then
    echo "✅ Memory updated successfully"
else
    echo "❌ Memory update not found"
fi

echo "🎉 All tests completed!"