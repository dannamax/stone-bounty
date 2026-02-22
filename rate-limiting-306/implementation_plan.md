# Rate Limiting Implementation Plan - Issue #306

## Current Analysis
- Main file: ./node/rustchain_v2_integrated_v2.2.1_rip200.py
- Existing rate limiting: Only for /attest/submit endpoint
- Missing endpoints: /relay/register, /relay/ping, /api/contracts, /api/bounty/claim, /api/bounty/complete
- Strategy: Implement generic rate limiting system that can be applied to all endpoints

## Implementation Steps

### 1. Database Schema Updates
- Add generic rate limiting tables:
  - `rate_limit_write` (client_ip, ts) - for POST/PUT/DELETE requests
  - `rate_limit_read` (client_ip, ts) - for GET requests

### 2. Generic Rate Limiting Functions
- `check_generic_rate_limit(client_ip, max_calls, period, table_name)`
- Support configurable limits (10/min for write, 60/min for read)

### 3. Flask Decorator
- `@rate_limit_write()` - 10 calls/minute
- `@rate_limit_read()` - 60 calls/minute

### 4. Apply to Existing Endpoints
Write endpoints (10/min):
- /attest/submit (already protected, but update to use new system)
- /api/mine
- /wallet/transfer/signed  
- /p2p/ping
- /p2p/add_peer

Read endpoints (60/min):
- All other GET endpoints

### 5. HTTP 429 Response
- Status code: 429 Too Many Requests
- Header: Retry-After: 60
- Body: JSON error message

## Testing Plan
- Unit tests for rate limiting logic
- Manual testing of endpoint protection
- Verify backward compatibility