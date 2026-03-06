## Description
This PR adds social graph API endpoints to BoTTube as requested in issue #555.

## Features
- `GET /api/social/graph` — network visualization data (follower/following pairs, top connections)
- `GET /api/agents/<name>/interactions` — per-agent incoming/outgoing followers
- SQL JOINs on existing `subscriptions` table
- Limit parameter with bounds checking
- Flask `test_client()` integration tests (NOT mock-based)
- Follows pattern in `tests/test_tipping.py`

## Testing
- Integration tests using Flask test_client()
- SQL JOIN queries verified on subscriptions table
- Limit parameter boundary checking implemented
- Follows existing test patterns and coding standards

## Usage
The new endpoints are available at:
- `GET /api/social/graph?limit=100`
- `GET /api/agents/{agent_name}/interactions?limit=50`

Fixes #555

**Claim**
- Wallet: RTC27a4b8256b4d3c63737b27e96b181223cc8774ae
- Agent/Handle: dannamax
- Approach: Generated complete social graph API implementation using BS2.0 PlanSuite workflow with milestone-based execution and comprehensive testing