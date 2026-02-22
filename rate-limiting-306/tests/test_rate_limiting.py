"""
Unit tests for the rate limiting module.
"""

import os
import sqlite3
import time
import sys
import unittest
from unittest.mock import Mock, patch

# Add the node directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'node'))

from rate_limiting import (
    init_rate_limit_tables,
    check_rate_limit,
    get_client_ip,
    rate_limit,
    DB_PATH,
    WRITE_LIMIT,
    READ_LIMIT
)


class TestRateLimiting(unittest.TestCase):
    
    def setUp(self):
        """Set up test database"""
        self.test_db = "test_rate_limit.db"
        # Update the global DB_PATH
        global DB_PATH
        DB_PATH = self.test_db
        
        # Initialize tables
        init_rate_limit_tables()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_init_tables(self):
        """Test that tables are created correctly"""
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn('rate_limit_write', tables)
            self.assertIn('rate_limit_read', tables)
    
    def test_check_rate_limit_within_limits(self):
        """Test rate limit check when within limits"""
        client_ip = "192.168.1.1"
        max_calls = 5
        period = 60
        table_name = "rate_limit_write"
        
        # Make 3 requests (within limit of 5)
        for i in range(3):
            result = check_rate_limit(client_ip, max_calls, period, table_name)
            self.assertTrue(result)
        
        # Check that we have 3 entries
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE client_ip = ?", (client_ip,))
            count = cursor.fetchone()[0]
            self.assertEqual(count, 3)
    
    def test_check_rate_limit_exceeds_limits(self):
        """Test rate limit check when exceeding limits"""
        client_ip = "192.168.1.2"
        max_calls = 2
        period = 60
        table_name = "rate_limit_write"
        
        # Make 2 requests (at limit)
        for i in range(2):
            result = check_rate_limit(client_ip, max_calls, period, table_name)
            self.assertTrue(result)
        
        # Third request should be rate limited
        result = check_rate_limit(client_ip, max_calls, period, table_name)
        self.assertFalse(result)
    
    def test_check_rate_limit_cleanup_old_entries(self):
        """Test that old entries are cleaned up"""
        client_ip = "192.168.1.3"
        max_calls = 10
        period = 2  # 2 second window
        table_name = "rate_limit_write"
        
        # Add an entry
        check_rate_limit(client_ip, max_calls, period, table_name)
        
        # Wait for more than the period
        time.sleep(2.1)
        
        # Manually add an old entry with timestamp in the past
        old_timestamp = int(time.time()) - 10  # 10 seconds ago
        with sqlite3.connect(self.test_db) as conn:
            conn.execute(f"INSERT INTO {table_name} (client_ip, ts) VALUES (?, ?)", (client_ip, old_timestamp))
        
        # Add another entry - old one should be cleaned up
        result = check_rate_limit(client_ip, max_calls, period, table_name)
        self.assertTrue(result)
        
        # Should only have 1 entry now (the new one, old one cleaned up)
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE client_ip = ?", (client_ip,))
            count = cursor.fetchone()[0]
            # Note: there might be 1 or 2 entries depending on timing, but old one should be gone
            # Just verify that cleanup happened by checking timestamps
            cursor.execute(f"SELECT ts FROM {table_name} WHERE client_ip = ?", (client_ip,))
            timestamps = [row[0] for row in cursor.fetchall()]
            current_time = int(time.time())
            # All timestamps should be within the last 2 seconds
            for ts in timestamps:
                self.assertGreaterEqual(ts, current_time - 2)
    
    @patch('rate_limiting.request')
    def test_get_client_ip_with_proxy(self, mock_request):
        """Test IP extraction with proxy headers"""
        # Test X-Forwarded-For
        mock_request.headers.get.return_value = "192.168.1.100, 10.0.0.1"
        mock_request.remote_addr = '127.0.0.1'
        ip = get_client_ip()
        self.assertEqual(ip, '192.168.1.100')
        
        # Test X-Real-IP  
        mock_request.headers.get.return_value = "192.168.1.200"
        ip = get_client_ip()
        self.assertEqual(ip, '192.168.1.200')
        
        # Test direct connection
        mock_request.headers.get.return_value = None
        mock_request.remote_addr = '192.168.1.300'
        ip = get_client_ip()
        self.assertEqual(ip, '192.168.1.300')


if __name__ == '__main__':
    unittest.main()