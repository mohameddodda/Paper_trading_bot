#!/usr/bin/env python3
"""
Multi-Bot Orchestrator Entry Point - Phase 5
Run multiple bots concurrently using core/bot_orchestrator.py
"""

from core.bot_orchestrator import BotOrchestrator
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch Multi-Bot Orchestration')
    parser.add_argument('--num-bots', type=int, default=2, help='Number of bots to run')
    parser.add_argument('--bots', nargs='+', default=['beast', 'cli'], help='Bot types')
    args = parser.parse_args()
    
    orch = BotOrchestrator(num_bots=args.num_bots, bot_types=args.bots)
    try:
        orch.start()
    except KeyboardInterrupt:
        orch.stop()
        print('Orchestrator stopped.')

