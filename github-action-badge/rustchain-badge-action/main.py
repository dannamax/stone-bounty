#!/usr/bin/env python3
"""
RustChain Mining Status Badge Generator
Generates shields.io compatible JSON for mining status badges
"""
import os
import sys
import json
import requests
from urllib.parse import quote

def get_mining_status(wallet_name: str, node_url: str = "http://50.28.86.131:8099") -> dict:
    """
    Get mining status from RustChain node
    
    Args:
        wallet_name: Miner wallet name
        node_url: RustChain node URL
        
    Returns:
        Dictionary with mining status information
    """
    try:
        # Get balance
        balance_url = f"{node_url}/balance/{quote(wallet_name)}"
        balance_resp = requests.get(balance_url, timeout=10)
        balance_data = balance_resp.json() if balance_resp.status_code == 200 else {}
        
        # Get epoch info
        epoch_url = f"{node_url}/epoch"
        epoch_resp = requests.get(epoch_url, timeout=10)
        epoch_data = epoch_resp.json() if epoch_resp.status_code == 200 else {}
        
        # Get miner attestation status
        miners_url = f"{node_url}/api/miners"
        miners_resp = requests.get(miners_url, timeout=10)
        miners_data = miners_resp.json() if miners_resp.status_code == 200 else []
        
        # Check if wallet is actively mining
        is_active = False
        if isinstance(miners_data, list):
            for miner in miners_data:
                if miner.get('miner') == wallet_name:
                    is_active = True
                    break
        
        # Extract data
        balance = balance_data.get('balance_rtc', 0)
        epoch = epoch_data.get('epoch', 0)
        status = "Active" if is_active else "Inactive"
        
        return {
            'balance': balance,
            'epoch': epoch,
            'status': status,
            'is_active': is_active
        }
    except Exception as e:
        print(f"Error fetching mining status: {e}", file=sys.stderr)
        return {
            'balance': 0,
            'epoch': 0,
            'status': 'Error',
            'is_active': False
        }

def generate_badge_json(status_data: dict) -> dict:
    """
    Generate shields.io compatible badge JSON
    
    Args:
        status_data: Mining status data from get_mining_status()
        
    Returns:
        Dictionary in shields.io endpoint format
    """
    balance = status_data['balance']
    epoch = status_data['epoch']
    status = status_data['status']
    
    # Format message
    message = f"{balance:.1f} RTC | Epoch {epoch} | {status}"
    
    # Determine color based on status
    if status == "Active":
        color = "brightgreen"
    elif status == "Inactive":
        color = "yellow"
    else:  # Error
        color = "red"
        message = "Error fetching status"
    
    return {
        "schemaVersion": 1,
        "label": "RustChain",
        "message": message,
        "color": color
    }

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <wallet_name> [node_url]", file=sys.stderr)
        sys.exit(1)
    
    wallet_name = sys.argv[1]
    node_url = sys.argv[2] if len(sys.argv) > 2 else "http://50.28.86.131:8099"
    
    status_data = get_mining_status(wallet_name, node_url)
    badge_json = generate_badge_json(status_data)
    
    print(json.dumps(badge_json, indent=2))

if __name__ == "__main__":
    main()