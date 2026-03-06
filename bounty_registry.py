#!/usr/bin/env python3
"""
Bounty Registry - Central registry for tracking all bounty opportunities and their status
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Bounty:
    """Represents a bounty opportunity"""
    id: str
    title: str
    url: str
    repository: str
    reward: str
    complexity: str  # LOW, MODERATE, HIGH, VERY_HIGH
    risk: str        # LOW, MEDIUM, HIGH
    time_estimate: str  # 1h, 2h, 6h, 24h, 168h
    type: str        # documentation, bug_fix, feature, test, community
    requirements: str
    status: str      # AVAILABLE, IN_PROGRESS, COMPLETED, SKIPPED
    created_at: str
    last_scanned: str
    bs2_score: int = 0
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW, SKIP

@dataclass
class BountyRegistryConfig:
    """Configuration for bounty registry"""
    scan_frequency_hours: int = 6
    max_concurrent_tasks: int = 3
    min_bs2_score: int = 30
    skip_complexity_threshold: str = "VERY_HIGH"
    auto_skip_risk_threshold: str = "HIGH"

class BountyRegistry:
    """Central registry for managing bounty opportunities"""
    
    def __init__(self, workspace_dir: str = "/home/admin/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.registry_file = self.workspace_dir / "bs2_tasks" / "bounty_registry.json"
        self.config_file = self.workspace_dir / "bs2_tasks" / "registry_config.json"
        self.config = self._load_config()
        self.bounties: Dict[str, Bounty] = {}
        self._load_registry()
    
    def _load_config(self) -> BountyRegistryConfig:
        """Load or create default configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_dict = json.load(f)
                return BountyRegistryConfig(**config_dict)
        else:
            config = BountyRegistryConfig()
            self._save_config(config)
            return config
    
    def _save_config(self, config: BountyRegistryConfig):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    
    def _load_registry(self):
        """Load bounty registry from file"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                self.bounties = {k: Bounty(**v) for k, v in data.items()}
    
    def _save_registry(self):
        """Save bounty registry to file"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.bounties.items()}, f, indent=2)
    
    def add_bounty(self, bounty: Bounty):
        """Add a new bounty to the registry"""
        self.bounties[bounty.id] = bounty
        self._save_registry()
    
    def update_bounty_status(self, bounty_id: str, status: str):
        """Update the status of a bounty"""
        if bounty_id in self.bounties:
            self.bounties[bounty_id].status = status
            self.bounties[bounty_id].last_scanned = datetime.now().isoformat()
            self._save_registry()
    
    def get_available_bounties(self) -> List[Bounty]:
        """Get all available bounties that meet criteria"""
        available = []
        for bounty in self.bounties.values():
            if (bounty.status == "AVAILABLE" and 
                bounty.bs2_score >= self.config.min_bs2_score and
                bounty.complexity != self.config.skip_complexity_threshold and
                bounty.risk != self.config.auto_skip_risk_threshold):
                available.append(bounty)
        return sorted(available, key=lambda x: x.bs2_score, reverse=True)
    
    def get_bounty_by_id(self, bounty_id: str) -> Optional[Bounty]:
        """Get a specific bounty by ID"""
        return self.bounties.get(bounty_id)
    
    def should_rescan(self) -> bool:
        """Check if it's time to rescan for new bounties"""
        if not self.bounties:
            return True
        
        latest_scan = max(b.last_scanned for b in self.bounties.values())
        latest_dt = datetime.fromisoformat(latest_scan.replace('Z', '+00:00'))
        return datetime.now() - latest_dt > timedelta(hours=self.config.scan_frequency_hours)
    
    def mark_all_as_scanned(self):
        """Mark all bounties as scanned"""
        current_time = datetime.now().isoformat()
        for bounty in self.bounties.values():
            bounty.last_scanned = current_time
        self._save_registry()