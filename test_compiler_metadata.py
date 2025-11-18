#!/usr/bin/env python3
"""Test script to verify compiler is using module metadata correctly."""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import compiler functions
try:
    from aibasic.aibasicc import get_all_task_types, get_task_type_info
    print("[OK] Successfully imported compiler functions")
except Exception as e:
    print(f"[FAIL] Failed to import compiler: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test get_all_task_types
print("\n=== Testing get_all_task_types() ===")
try:
    all_types = get_all_task_types()
    print(f"[OK] Found {len(all_types)} task types")

    # Check if discord is present
    if 'discord' in all_types:
        print("\n[OK] Discord task type found")
        discord_info = all_types['discord']
        print(f"  Name: {discord_info.get('name')}")
        print(f"  Description: {discord_info.get('description')}")
        print(f"  Has module_metadata: {'module_metadata' in discord_info}")

        if 'module_metadata' in discord_info:
            module_meta = discord_info['module_metadata']
            print(f"  Metadata keys: {list(module_meta.keys())}")
            print(f"  Methods: {len(module_meta.get('methods', []))}")
            print(f"  Usage notes: {len(module_meta.get('usage_notes', []))}")
            print(f"  Examples: {len(module_meta.get('examples', []))}")
    else:
        print("\n[WARN] Discord task type NOT found in combined types")

    # Check if telegram is present
    if 'telegram' in all_types:
        print("\n[OK] Telegram task type found")
        telegram_info = all_types['telegram']
        print(f"  Name: {telegram_info.get('name')}")
        print(f"  Has module_metadata: {'module_metadata' in telegram_info}")
        if 'module_metadata' in telegram_info:
            module_meta = telegram_info['module_metadata']
            print(f"  Methods: {len(module_meta.get('methods', []))}")
    else:
        print("\n[WARN] Telegram task type NOT found in combined types")

except Exception as e:
    print(f"[FAIL] Error getting task types: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test get_task_type_info for discord
print("\n=== Testing get_task_type_info('discord') ===")
try:
    discord_info = get_task_type_info('discord')
    print(f"[OK] Got discord task info")
    print(f"  Name: {discord_info.get('name')}")
    print(f"  Description: {discord_info.get('description')[:100]}...")
    print(f"  Keywords: {discord_info.get('keywords')}")
    print(f"  Has module_metadata: {'module_metadata' in discord_info}")

    if 'module_metadata' in discord_info:
        print("\n[OK] Module metadata is available to compiler!")
    else:
        print("\n[WARN] Module metadata NOT available to compiler")

except Exception as e:
    print(f"[FAIL] Error getting discord info: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
