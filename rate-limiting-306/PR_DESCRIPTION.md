## Security Bounty: Add Rate Limiting to Beacon Atlas API — 8 RTC

This PR implements comprehensive rate limiting for the Beacon Atlas API endpoints, addressing the security vulnerability where attackers could abuse the API endpoints through excessive requests.

### Implementation Details

#### ✅ Generic Rate Limiting Module
- **File**: `node/rate_limiting.py`
- **Algorithm**: Sliding window rate limiting with SQLite backend
- **Persistence**: Works across gunicorn workers using shared SQLite database
- **No External Dependencies**: Pure Python implementation as required

#### ✅ Configurable Limits
- **Write Operations** (`POST`, `PUT`, `DELETE`): **10 requests per minute**
- **Read Operations** (`GET`): **60 requests per minute**
- **HTTP 429 Response**: Returns proper error code with `Retry-After` header

#### ✅ Applied to All Relevant Endpoints
Based on analysis of the existing codebase, I've applied rate limiting to all write endpoints that match the Issue #306 requirements:

**Protected Write Endpoints (10/min)**:
- `/attest/submit` - Hardware attestation submission
- `/api/mine` - Mining operations  
- `/wallet/transfer/signed` - Wallet transfers
- `/p2p/ping` - P2P network ping
- `/p2p/add_peer` - P2P peer addition

**Protected Read Endpoints (60/min)**:
- `/api/stats` - Statistics endpoint
- `/api/nodes` - Node information
- `/api/miners` - Miner information
- `/api/balances` - Balance queries
- All other GET endpoints

#### ✅ Integration Approach
Since the exact endpoints mentioned in Issue #306 (`/relay/register`, `/relay/ping`, `/api/contracts`, etc.) don't exist in the current codebase, I've implemented a **comprehensive solution** that:

1. **Protects all existing write endpoints** that could be abused
2. **Provides a reusable decorator** for future endpoints
3. **Follows the same pattern** as the existing `check_ip_rate_limit()` function
4. **Uses the same database** (`beacon_atlas.db`) for consistency

#### ✅ Backward Compatibility
- **Non-breaking**: Existing functionality remains unchanged
- **Graceful degradation**: If rate limiting fails, requests are still processed
- **Same IP detection**: Uses identical IP extraction logic as existing code

### Key Features

1. **Security First**: Prevents DoS and API abuse attacks
2. **Scalable**: Works with multiple gunicorn workers using shared SQLite
3. **Configurable**: Easy to adjust limits or add new endpoint types
4. **Well-Tested**: Includes comprehensive unit tests
5. **Maintainable**: Clean, documented code following RustChain standards

### Usage Examples

```python
from rate_limiting import rate_limit

# Apply write rate limiting (10/min)
@app.route('/api/new-endpoint', methods=['POST'])
@rate_limit(calls_per_minute=10, key_prefix="write")
def new_write_endpoint():
    return jsonify({"status": "ok"})

# Apply read rate limiting (60/min)  
@app.route('/api/new-read', methods=['GET'])
@rate_limit(calls_per_minute=60, key_prefix="read")
def new_read_endpoint():
    return jsonify({"data": "info"})
```

### Testing

The included test suite covers:
- Table initialization and database setup
- Rate limit enforcement within limits
- Rate limit blocking when exceeded
- Proper HTTP 429 responses with Retry-After headers
- IP address extraction from proxy headers

### Dependencies

- **None**: Uses only standard library and existing Flask dependencies
- **SQLite**: Leverages existing database infrastructure

This implementation provides immediate protection against API abuse while maintaining full compatibility with the existing RustChain ecosystem.

Fixes #306

Reward: 8 RTC