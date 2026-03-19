# Stone Bounty - Automated GitHub Bounty Hunter

## Description
Stone Bounty is an automated system that identifies, analyzes, and submits high-quality contributions to GitHub repositories with bounty programs. The system focuses on documentation improvements, small bug fixes, and feature enhancements with monetary rewards.

## Key Features
- 🔍 **Bounty Discovery**: Automatically finds issues with bounty/reward labels
- 🎯 **Smart Filtering**: Avoids complex projects (blacklisted: rust-lang/rust, vuejs/vue, etc.)
- ✅ **Quality Control**: Ensures actual code changes, not template comments
- 📊 **Success Tracking**: Monitors PR status and bounty claims
- ⚠️ **Emergency Stop**: Manual-only mode for high-quality contributions

## Strategy
- Focus on small, achievable tasks (docs, tests, minor fixes)
- Avoid large/complex projects requiring CLA or deep expertise
- Manual review required before any PR submission
- Success rate target: >25% (currently 12.5%)

## Current Status
- ✅ **Active PR**: Scottcjn/Rustchain #247 (75 RTC awaiting review)
- ✅ **Completed**: Scottcjn/Rustchain #139 (10 RTC claimed)
- ⚠️ **Emergency Stop**: All automation disabled, manual-only mode active

## Setup
```bash
# Clone the skill
git clone https://github.com/your-repo/stone-bounty.git
# Install dependencies
cd stone-bounty && ./scripts/setup.sh
# Configure your GitHub token
echo "your_github_token" > .github_token
# Set your wallet address
echo "your_wallet_address" > .wallet_address
```

## Usage
```bash
# Monitor for new opportunities (manual review required)
./scripts/bounty_monitor.sh --manual-only

# Submit a PR (after manual verification)
./scripts/pr_submitter.sh --issue-url "https://github.com/repo/issue/123"

# Validate contribution quality
./scripts/validator.sh --pr-url "https://github.com/repo/pull/456"
```

## Configuration
Edit `config/automation_config.json` to customize behavior:
- `emergency_stop_active`: true (recommended)
- `manual_only_mode`: true (required for quality)
- `max_daily_submissions`: 0 (disabled in emergency mode)

## Safety Guidelines
- Never submit automated/template PRs
- Always verify issue has clear bounty amount
- Avoid projects requiring CLA agreements
- Focus on documentation and small improvements
- Manual review required for all submissions

## Success Metrics
- Target success rate: >25%
- Current success rate: 12.5% (1/8)
- Active bounties: 1 (Rustchain #213)
- Total claimed: 10 RTC

## License
MIT License - Use responsibly and contribute quality work.