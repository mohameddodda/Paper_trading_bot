cat > CHANGELOG.md << ‘EOF’
# Changelog

All notable changes to **Paper Trading Bot** will be documented here.

## [v1.2.1] - 2025-11-15

### Added
- **XRP_USDT** and **ADA_USDT** to supported symbols
- **Voice alerts** on trade execution (iOS)
- **Backtesting** with `backtest.py` (Crypto.com public data)
- **RL training** with `train_rl.py` (Stable-Baselines3, desktop)
- **Console UI** with live price chart (sparklines)

### Changed
- Switched from **Polygon** → **Crypto.com public API** (no key)
- **Dual licensing**: MIT OR Apache-2.0
- **$1M virtual balance** (from $10k)

### Security
- API key stored in **Keychain** only
- `.env` gitignored

—

## [v1.2.0] - 2025-11-10

### Added
- **OpenRouter + DeepSeek AI** for trade signals
- **Push notifications** on trades
- **CSV trade logging**

—

*Follows [Keep a Changelog](https://keepachangelog.com/)*
EOF

git add CHANGELOG.md
git commit -m “docs: add CHANGELOG.md with v1.2.1”