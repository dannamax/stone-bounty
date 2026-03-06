#!/usr/bin/env python3
"""
Historical Projects Blocklist for BS2.0
Automatically skips known historical projects that should not be processed.
"""

# List of historical issue numbers that should be skipped
HISTORICAL_ISSUE_NUMBERS = {
    # Rustchain-bounties historical issues
    165, 167, 304, 308, 311, 329, 334, 335, 336, 337,
    # Other historical issues that were already processed
    23, 24, 27, 28, 31, 32, 48, 159, 160, 164, 166, 168, 169, 171,
    255, 256, 299, 285
}

# Keywords that indicate historical/repeat projects
HISTORICAL_KEYWORDS = [
    "retroactive", "backfill", "historical", "legacy", 
    "already submitted", "previously completed", "duplicate",
    "architecture error", "wrong repository"
]

def should_skip_historical_issue(issue_number: int, title: str, description: str) -> bool:
    """Check if an issue should be skipped as historical"""
    # Check issue number
    if issue_number in HISTORICAL_ISSUE_NUMBERS:
        return True
    
    # Check keywords in title and description
    combined_text = f"{title} {description}".lower()
    for keyword in HISTORICAL_KEYWORDS:
        if keyword in combined_text:
            return True
    
    return False

if __name__ == "__main__":
    # Test the blocklist
    test_cases = [
        (311, "feat(xp): retroactive XP + badge backfill", ""),
        (500, "New bounty opportunity", "Fresh new task"),
        (308, "signature verification", "focused implementation")
    ]
    
    for issue_num, title, desc in test_cases:
        skip = should_skip_historical_issue(issue_num, title, desc)
        print(f"Issue #{issue_num}: {title} -> Skip: {skip}")