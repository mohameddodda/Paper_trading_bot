#!/usr/bin/env python3
"""Security dependency scan using Safety."""
import subprocess
import sys
from pathlib import Path

def main():
    safety_cmd = ['safety', 'check', '--full-report']
    result = subprocess.run(safety_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print('✅ All dependencies are safe!')
    else:
        print('⚠️  Security issues found:')
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
