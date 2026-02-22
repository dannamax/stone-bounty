## GitHub Action: RustChain Mining Status Badge — 40 RTC

This PR implements Issue #256 by adding a `/api/badge/<wallet>` endpoint to the RustChain node and providing a minimal GitHub Action.

### Changes Made

#### ✅ Added Badge API Endpoint
- Directly added `/api/badge/<wallet>` route to `rustchain_v2_integrated_v2.2.1_rip200.py`
- Returns shields.io compatible JSON format for mining status badges
- Includes wallet balance, current epoch, and mining activity status
- Safe database queries that handle different schema versions
- Proper error handling and validation

#### ✅ Minimal GitHub Action Implementation  
- Created `action.yml` with proper metadata
- Implemented `index.js` for badge updating functionality
- No unnecessary files or directories

#### ✅ Correct Documentation
- Added usage instructions to README.md
- Only documents actual implemented functionality
- No modifications to SECURITY.md or other legal files
- Removed all Beacon Atlas endpoint references (not part of RustChain node)

### Technical Details

**Badge Endpoint Features:**
- **Wallet Validation**: Basic validation without arbitrary length restrictions
- **Schema Compatibility**: Safely handles different database schema versions
- **Activity Detection**: Checks for recent attestations (last hour) to determine active/inactive status  
- **Proper Formatting**: Returns correct shields.io JSON format with appropriate colors
- **Error Handling**: Graceful error handling with 500 responses for unexpected issues

**GitHub Action Features:**
- Updates README with current mining status badge
- Configurable wallet parameter
- Compatible with shields.io endpoint format

### Testing

- Verified badge endpoint returns correct JSON format
- Confirmed database queries work with different schema versions  
- Tested wallet validation with various input types
- Validated GitHub Action workflow integration

Fixes #256

Reward: 40 RTC