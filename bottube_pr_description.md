## Description
This PR adds social graph API endpoints to BoTTube as requested in issue #555.

## Features
- `GET /api/social/graph` — network visualization data (follower/following pairs, top connections)
- `GET /api/agents/<name>/interactions` — per-agent incoming/outgoing followers
- SQL JOINs on existing `subscriptions` table
- Limit parameter with bounds checking
- Flask `test_client()` integration tests (NOT mock-based)
- Follow pattern in `tests/test_tipping.py`

## Testing
- Integration tests using Flask test_client()
- SQL JOIN queries verified on subscriptions table
- Limit parameter boundary checking implemented
- All endpoints return correct data structure

Fixes #555

**Claim**
- Wallet: RTC27a4b8256b4d3c63737b27e96b181223cc8774ae
- Agent/Handle: dannamax
- Approach: Implemented complete social graph API with integration tests following BS2.0 design principles and PlanSuite milestone workflow
