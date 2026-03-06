#!/usr/bin/env python3
"""
BS2.0 Automated Bounty System Configuration
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class AutoBountyConfig:
    """Automated bounty system configuration"""
    
    # Discovery settings
    scan_frequency_hours: int = 6  # How often to scan for new bounties
    max_bounties_per_cycle: int = 5  # Max bounties to process per cycle
    bounty_sources: List[str] = field(default_factory=list)
    
    # Analysis settings
    min_bs2_score: int = 30  # Minimum BS2 score to consider
    skip_complexity_levels: List[str] = field(default_factory=lambda: ["VERY_HIGH"])
    max_time_estimate_hours: int = 168  # Max time estimate to consider (7 days)
    
    # PR generation settings
    auto_pr_enabled: bool = True
    pr_template_dir: str = "templates/pr"
    wallet_address: str = "RTC27a4b8256b4d3c63737b27e96b181223cc8774ae"
    github_username: str = "dannamax"
    github_token: str = ""
    
    # Safety settings
    dry_run_mode: bool = False  # Set to True for testing
    require_manual_approval: bool = False  # Require manual approval for PRs
    max_concurrent_tasks: int = 3  # Max concurrent automated tasks
    
    # Notification settings
    notify_on_new_bounty: bool = True
    notify_on_pr_created: bool = True
    notify_on_bounty_claimed: bool = True
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'AutoBountyConfig':
        """Load configuration from JSON file"""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
                return cls(**data)
        else:
            # Return default config
            config = cls()
            config.bounty_sources = [
                "https://github.com/Scottcjn/rustchain-bounties",
                "https://github.com/openclaw/openclaw"
            ]
            return config
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=str)

# Default configuration
DEFAULT_CONFIG = AutoBountyConfig()