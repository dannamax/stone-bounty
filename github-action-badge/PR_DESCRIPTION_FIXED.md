Implements Issue #256: GitHub Action for RustChain mining status badges. Includes API endpoint and complete GitHub Action.

## Fixes from maintainer review

This PR addresses the blocking issues identified in the initial review:

### ✅ Fixed: Documentation/Runtime Mismatch
- Removed incorrect references to `/relay/register` and `/relay/ping` endpoints from RustChain documentation
- These endpoints belong to the beacon-skill Atlas service, not the RustChain node
- Updated documentation to accurately reflect available RustChain API endpoints only

### ✅ Fixed: Wallet ID Length Validation  
- Removed overly restrictive `len(wallet) < 10` validation
- Now accepts all valid wallet IDs regardless of length
- Maintains basic validation (`if not wallet or not wallet.strip()`)

### ✅ Fixed: Schema-Fragile Badge Query
- Replaced fragile query that referenced potentially missing columns
- Implemented robust column detection with fallback logic
- Prevents 500 errors on mixed deployment schemas
- Uses dynamic query construction based on actual table structure

## Implementation Details

### GitHub Action Features
- **Shields.io Integration**: Returns badge JSON in shields.io format
- **Real-time Status**: Shows wallet balance, current epoch, and mining activity
- **Automatic Updates**: Can auto-update README files with current mining status
- **Marketplace Ready**: Complete action.yml with proper metadata

### API Endpoint (`/api/badge/<wallet>`)
- Returns shields.io-compatible JSON response
- Validates wallet parameter safely
- Queries balance from database with schema-aware logic
- Determines mining status (Active/Inactive) based on recent attestations
- Returns appropriate color coding (brightgreen/yellow/orange/red)

### Security & Reliability
- Proper error handling with 500 status codes
- Input validation without false rejections
- Database connection management with context managers
- Schema compatibility across different RustChain deployments

Fixes #256

Reward: 40 RTC