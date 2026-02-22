# RustChain Mining Status Badge GitHub Action

![RustChain Mining](https://img.shields.io/endpoint?url=https://50.28.86.131/api/badge/frozen-factorio-ryan)

This GitHub Action displays a live RustChain mining status badge in your repository README, showing your miner wallet balance, current epoch, and mining status.

## Features

- **Live Mining Status**: Real-time badge showing your RustChain mining status
- **Shields.io Integration**: Compatible with shields.io endpoint format
- **Automatic README Updates**: Optional GitHub Action to auto-update your README
- **Marketplace Ready**: Published to GitHub Marketplace for easy discovery

## Usage

### Option 1: Direct Badge Link (No Action Required)

Add this to your README.md:

```markdown
![RustChain Mining](https://img.shields.io/endpoint?url=https://50.28.86.131/api/badge/YOUR_WALLET_NAME)
```

Replace `YOUR_WALLET_NAME` with your actual RustChain miner wallet name.

### Option 2: GitHub Action (Auto-updates README)

Add this workflow to `.github/workflows/rustchain-badge.yml`:

```yaml
name: RustChain Mining Badge
on:
  schedule:
    - cron: '*/30 * * * *'  # Update every 30 minutes
  workflow_dispatch:  # Allow manual trigger

jobs:
  update-badge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: Scottcjn/rustchain-badge-action@v1
        with:
          wallet: YOUR_WALLET_NAME
          readme-path: README.md  # Optional, defaults to README.md
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Update RustChain mining badge" || echo "No changes to commit"
          git push
```

## Badge JSON Format

The API endpoint returns shields.io-compatible JSON:

```json
{
  "schemaVersion": 1,
  "label": "RustChain",
  "message": "42.5 RTC | Epoch 73 | Active",
  "color": "brightgreen"
}
```

## Configuration

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `wallet` | Yes | N/A | Your RustChain miner wallet name |
| `readme-path` | No | `README.md` | Path to README file to update |

## Security

- Uses HTTPS for all API calls
- No sensitive data stored or transmitted
- Read-only access to your repository

## Support

For issues or feature requests, please open an issue on the [RustChain repository](https://github.com/Scottcjn/Rustchain).

## License

MIT License