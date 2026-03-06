#!/bin/bash
# Auto Bounty Hunter Cron Script
# Runs every 6 hours to scan for new bounty opportunities

cd /home/admin/.openclaw/workspace/external_storage/bs2_system
source /home/admin/.bashrc

echo "[$(date)] Starting automated bounty scan..."
python3 run_auto_bounty_hunter.py --scan-only

echo "[$(date)] Automated bounty scan completed."