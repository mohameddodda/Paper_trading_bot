# Fix Test Errors Plan
## Steps:
- [ ] Step 1: Fix core/db_manager.py (add get_recent_trades, fix get_trade_stats SQL)
- [ ] Step 2: Fix core/bot_orchestrator.py (add 'cli' support, singleton DB)
- [ ] Step 3: Update tests/test_orchestration.py if needed
- [ ] Step 4: Test with pytest tests/test_db.py -v && pytest tests/test_orchestration.py -v
- [ ] Step 5: Full pytest tests/ -v
- [ ] Step 6: attempt_completion

