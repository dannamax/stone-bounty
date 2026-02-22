#!/usr/bin/env python3
"""
Complete test for RustChain badge functionality
Tests both old and new database schema versions
"""

import sqlite3
import json
import os
import time
from datetime import datetime

# Test wallet
TEST_WALLET = "frozen-factorio-ryan"
DB_PATH = "test_rustchain_v2.db"

def create_test_db():
    """Create test database with both old and new schema"""
    print("🔧 Creating test database...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create both schema versions
    # Old schema
    c.execute("""
        CREATE TABLE IF NOT EXISTS balances_old (
            miner_pk TEXT PRIMARY KEY, 
            balance_rtc REAL DEFAULT 0
        )
    """)
    
    # New schema  
    c.execute("""
        CREATE TABLE IF NOT EXISTS balances_new (
            miner_id TEXT PRIMARY KEY,
            amount_i64 INTEGER
        )
    """)
    
    # Epoch table
    c.execute("""
        CREATE TABLE IF NOT EXISTS epoch_state (
            epoch INTEGER PRIMARY KEY, 
            accepted_blocks INTEGER DEFAULT 0, 
            finalized INTEGER DEFAULT 0
        )
    """)
    
    # Attestation table
    c.execute("""
        CREATE TABLE IF NOT EXISTS miner_attest_recent (
            miner TEXT PRIMARY KEY,
            ts_ok INTEGER,
            device_family TEXT,
            device_arch TEXT,
            entropy_score REAL,
            fingerprint_passed INTEGER,
            source_ip TEXT
        )
    """)
    
    # Insert test data
    balance_rtc = 42.5
    balance_urtc = int(balance_rtc * 1000000)  # micro-units
    
    # Old schema data
    c.execute("INSERT OR REPLACE INTO balances_old (miner_pk, balance_rtc) VALUES (?, ?)", 
              (TEST_WALLET, balance_rtc))
    
    # New schema data  
    c.execute("INSERT OR REPLACE INTO balances_new (miner_id, amount_i64) VALUES (?, ?)", 
              (TEST_WALLET, balance_urtc))
    
    # Epoch data
    current_epoch = 73
    c.execute("INSERT OR REPLACE INTO epoch_state (epoch, accepted_blocks, finalized) VALUES (?, ?, ?)", 
              (current_epoch, 100, 1))
    
    # Attestation data (active miner)
    now = int(time.time())
    c.execute("""
        INSERT OR REPLACE INTO miner_attest_recent 
        (miner, ts_ok, device_family, device_arch, entropy_score, fingerprint_passed, source_ip)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (TEST_WALLET, now, "x86_64", "modern", 0.5, 1, "127.0.0.1"))
    
    conn.commit()
    conn.close()
    print("✅ Test database created successfully")

def get_balance_from_db(wallet_id, db_path):
    """Get balance from database (handles both schemas)"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Try new schema first
    try:
        c.execute("SELECT amount_i64 FROM balances_new WHERE miner_id = ?", (wallet_id,))
        row = c.fetchone()
        if row and row[0] is not None:
            balance_rtc = row[0] / 1000000.0
            conn.close()
            return balance_rtc
    except sqlite3.Error:
        pass
    
    # Try old schema
    try:
        c.execute("SELECT balance_rtc FROM balances_old WHERE miner_pk = ?", (wallet_id,))
        row = c.fetchone()
        if row and row[0] is not None:
            conn.close()
            return float(row[0])
    except sqlite3.Error:
        pass
    
    conn.close()
    return 0.0

def get_current_epoch(db_path):
    """Get current epoch from database"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT epoch FROM epoch_state ORDER BY epoch DESC LIMIT 1")
        row = c.fetchone()
        if row:
            conn.close()
            return row[0]
    except sqlite3.Error:
        pass
    
    conn.close()
    return 0

def is_miner_active(wallet_id, db_path):
    """Check if miner is active (attested in last hour)"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        now = int(time.time())
        one_hour_ago = now - 3600
        
        c.execute("SELECT ts_ok FROM miner_attest_recent WHERE miner = ? AND ts_ok > ?", 
                  (wallet_id, one_hour_ago))
        row = c.fetchone()
        conn.close()
        return row is not None
    except sqlite3.Error:
        conn.close()
        return False

def generate_badge_json(wallet_id, db_path):
    """Generate badge JSON for shields.io"""
    balance = get_balance_from_db(wallet_id, db_path)
    epoch = get_current_epoch(db_path)
    is_active = is_miner_active(wallet_id, db_path)
    
    status = "Active" if is_active else "Inactive"
    message = f"{balance:.1f} RTC | Epoch {epoch} | {status}"
    
    # Color based on activity
    color = "brightgreen" if is_active else "red"
    
    badge_data = {
        "schemaVersion": 1,
        "label": "RustChain",
        "message": message,
        "color": color
    }
    
    return badge_data

def main():
    """Main test function"""
    print("🧪 Testing complete badge functionality...")
    
    # Clean up any existing test DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Create test database
    create_test_db()
    
    # Test badge generation
    badge = generate_badge_json(TEST_WALLET, DB_PATH)
    
    print("✅ Badge JSON generated:")
    print(json.dumps(badge, indent=2))
    
    # Validate required fields
    required_fields = ["schemaVersion", "label", "message", "color"]
    for field in required_fields:
        if field not in badge:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Validate message format
    expected_parts = ["RTC", "Epoch", "Active"]
    message = badge["message"]
    for part in expected_parts:
        if part not in message:
            print(f"❌ Message format incorrect: missing '{part}'")
            return False
    
    print("✅ All tests passed!")
    
    # Clean up
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Badge functionality test completed successfully!")
    else:
        print("\n❌ Badge functionality test failed!")
        exit(1)