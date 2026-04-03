# Copyright 2026 Mohamed Dodda
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
setup_dirs.py – Directory Setup Script
======================================

Creates the necessary directory structure for the Paper Trading Bot.
Run: python setup_dirs.py
"""

import os
from pathlib import Path

def create_directories():
    """Create all required directories."""
    root = Path(__file__).parent.resolve()
    
    dirs = [
        'core',
        'bots',
        'training',
        'config',
        'docs',
        'scripts',
        'tests',
        'assets',
    ]
    
    print("Creating directory structure...")
    for d in dirs:
        path = root / d
        path.mkdir(exist_ok=True)
        print(f"  ✓ {d}/")
    
    # Create __init__.py files for Python packages
    init_files = [
        'core/__init__.py',
        'bots/__init__.py',
        'training/__init__.py',
        'config/__init__.py',
    ]
    
    print("\nCreating __init__.py files...")
    for init_file in init_files:
        path = root / init_file
        path.touch(exist_ok=True)
        print(f"  ✓ {init_file}")
    
    print("\n✅ Directory structure created successfully!")

if __name__ == "__main__":
    create_directories()
