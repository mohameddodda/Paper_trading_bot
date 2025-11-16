# Bot Improvement TODO

## 1. Create Configuration File
- [x] Create `config.json` with symbols, intervals, risk settings, etc.

## 2. Update Dependencies
- [x] Update `requirements.txt` to include Flask

## 3. Enhance Security & Config
- [x] Modify `get_api_key()` to check `OPENROUTER_API_KEY` env var first
- [x] Load settings from `config.json`

## 4. Improve Performance
- [x] Add price caching with 10-second TTL
- [x] Optimize API calls

## 5. Better Error Handling
- [x] Add retries and exponential backoff for API failures
- [x] Graceful degradation on errors

## 6. Enhance AI Signals
- [ ] Add trend analysis (SMA, RSI-like) to AI prompt
- [ ] Improve prompt instructions for better signals

## 7. Add Web Dashboard
- [ ] Integrate Flask app for monitoring
- [ ] Add routes for status, portfolio, logs

## 8. Testing
- [ ] Test bot functionality with new features
- [ ] Test web dashboard at localhost:5000
