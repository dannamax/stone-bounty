## 🎯 GitHub Action: RustChain Mining Status Badge — 40 RTC

This PR implements the complete GitHub Action for RustChain mining status badges as specified in Issue #256.

### ✅ Features Implemented

#### **1. Badge API Endpoint**
- Added `/api/badge/<wallet>` endpoint to RustChain node
- Returns shields.io-compatible JSON format
- Includes miner balance, current epoch, and mining status
- Proper error handling for invalid wallets

#### **2. GitHub Action**
- Complete GitHub Action with `action.yml`
- Automatic README badge updates
- Configurable wallet parameter
- Marketplace-ready with proper metadata

#### **3. Usage Examples**

**Direct Badge Link:**
```markdown
![RustChain Mining](https://img.shields.io/endpoint?url=https://50.28.86.131/api/badge/frozen-factorio-ryan)
```

**GitHub Action:**
```yaml
- uses: Scottcjn/rustchain-badge-action@v1
  with:
    wallet: my-wallet-name
```

### 🔧 Technical Details

#### **Badge JSON Format (shields.io compatible):**
```json
{
  "schemaVersion": 1,
  "label": "RustChain",
  "message": "42.5 RTC | Epoch 73 | Active",
  "color": "brightgreen"
}
```

#### **API Endpoint:**
- Route: `GET /api/badge/<wallet>`
- Returns 404 for invalid wallets
- Caches database queries for performance
- Handles both miner_pk and miner_id formats

#### **GitHub Action Components:**
- `action.yml`: Action metadata and inputs
- `index.js`: Main action logic
- `package.json`: Dependencies and scripts
- Comprehensive README with examples

### 🧪 Testing

- ✅ Badge JSON format validation
- ✅ API endpoint error handling
- ✅ GitHub Action functionality
- ✅ shields.io integration compatibility
- ✅ README auto-update capability

### 📦 Ready for Marketplace

- Complete action structure with proper metadata
- Comprehensive documentation
- Working examples and test cases
- Follows GitHub Action best practices

### 💰 Reward
**40 RTC** for complete implementation and Marketplace publication

Fixes #256