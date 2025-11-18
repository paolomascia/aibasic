#!/usr/bin/env python3
"""Test script to verify module metadata system works correctly."""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test importing the module_base functions
try:
    from aibasic.modules.module_base import collect_all_modules_metadata, generate_prompt_context
    print("[OK] Successfully imported module_base functions")
except Exception as e:
    print(f"[FAIL] Failed to import module_base: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test collecting metadata
try:
    print("\n=== Collecting Module Metadata ===")
    metadata = collect_all_modules_metadata()
    print(f"[OK] Collected metadata for {len(metadata)} modules")
    print(f"  Available task types: {', '.join(sorted(metadata.keys()))}")
except Exception as e:
    print(f"[FAIL] Failed to collect metadata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Discord module specifically
if 'discord' in metadata:
    print("\n=== Discord Module Metadata ===")
    discord_doc = metadata['discord']
    discord_meta = discord_doc['metadata']
    print(f"  Name: {discord_meta['name']}")
    print(f"  Task Type: {discord_meta['task_type']}")
    print(f"  Description: {discord_meta['description']}")
    print(f"  Version: {discord_meta['version']}")
    print(f"  Keywords: {', '.join(discord_meta['keywords'])}")
    print(f"  Dependencies: {', '.join(discord_meta['dependencies'])}")
    print(f"  Methods: {len(discord_doc['methods'])}")
    print(f"  Usage Notes: {len(discord_doc['usage_notes'])}")
    print(f"  Examples: {len(discord_doc['examples'])}")

    # Test generate_prompt_context
    print("\n=== Testing generate_prompt_context for Discord ===")
    try:
        context = generate_prompt_context('discord')
        print(f"[OK] Generated context ({len(context)} characters)")
        print("\n--- First 500 characters ---")
        print(context[:500])
        print("...")
    except Exception as e:
        print(f"[FAIL] Failed to generate context: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n[WARN] Discord module metadata not found")

# Test Telegram module
if 'telegram' in metadata:
    print("\n=== Telegram Module Metadata ===")
    telegram_doc = metadata['telegram']
    telegram_meta = telegram_doc['metadata']
    print(f"  Name: {telegram_meta['name']}")
    print(f"  Methods: {len(telegram_doc['methods'])}")
else:
    print("\n[WARN] Telegram module metadata not found (needs implementation)")

print("\n=== Test Complete ===")
