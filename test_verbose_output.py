#!/usr/bin/env python3
"""
Test script to verify verbose output when explicit task type is detected.
This script simulates compilation without calling the actual LLM API.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aibasic.aibasicc import (
    parse_instruction,
    get_task_type_info,
    detect_task_type
)

print("=" * 80)
print("TEST: Verbose Output for Explicit Task Types")
print("=" * 80)

# Test instructions with explicit task types
test_instructions = [
    '10 (discord) send message "Hello World"',
    '20 (telegram) send notification with title "Test" and level "success"',
    '30 (postgres) query all users from database',
    '40 send webhook to discord',  # No explicit type
]

for instruction_line in test_instructions:
    print(f"\n{'=' * 80}")
    print(f"Processing: {instruction_line}")
    print(f"{'=' * 80}")

    # Parse instruction
    line_num, instr_text, explicit_task_type, jump_target, is_unconditional, error_handler, call_target, is_return = parse_instruction(instruction_line)

    print(f"\n--- Parsed Instruction {line_num} ---")
    print(f"Text: {instr_text}")

    if explicit_task_type:
        print(f"\n[TASK TYPE] Explicit: ({explicit_task_type})")

        # Get detailed task type information
        task_info = get_task_type_info(explicit_task_type)
        print(f"[TASK TYPE] Name: {task_info.get('name', 'Unknown')}")
        print(f"[TASK TYPE] Description: {task_info.get('description', 'N/A')}")

        # Check if module has rich metadata
        if 'module_metadata' in task_info:
            module_meta = task_info['module_metadata']
            metadata = module_meta.get('metadata', {})
            print(f"\n[METADATA] ✓ Rich module metadata available")
            print(f"[METADATA]   Version: {metadata.get('version', 'N/A')}")
            print(f"[METADATA]   Methods: {len(module_meta.get('methods', []))}")
            print(f"[METADATA]   Usage Notes: {len(module_meta.get('usage_notes', []))}")
            print(f"[METADATA]   Examples: {len(module_meta.get('examples', []))}")
            print(f"[METADATA]   Dependencies: {', '.join(metadata.get('dependencies', []))}")

            # Print methods
            methods = module_meta.get('methods', [])
            if methods:
                print(f"\n[METADATA]   Available methods:")
                for method in methods[:5]:  # Show first 5 methods
                    method_name = method.get('name', 'unknown')
                    method_desc = method.get('description', '')[:60]
                    print(f"[METADATA]     - {method_name}: {method_desc}")
                if len(methods) > 5:
                    print(f"[METADATA]     ... and {len(methods) - 5} more")

            # Show usage notes sample
            usage_notes = module_meta.get('usage_notes', [])
            if usage_notes:
                print(f"\n[METADATA]   Sample usage notes:")
                for note in usage_notes[:3]:
                    print(f"[METADATA]     • {note}")
                if len(usage_notes) > 3:
                    print(f"[METADATA]     ... and {len(usage_notes) - 3} more")

            # Show examples sample
            examples = module_meta.get('examples', [])
            if examples:
                print(f"\n[METADATA]   Sample AIbasic examples:")
                for example in examples[:3]:
                    print(f"[METADATA]     {example}")
                if len(examples) > 3:
                    print(f"[METADATA]     ... and {len(examples) - 3} more")

            # Simulate prompt generation
            from aibasic.modules.module_base import generate_prompt_context
            try:
                prompt_context = generate_prompt_context(explicit_task_type)
                print(f"\n[PROMPT] Generated rich prompt context:")
                print(f"[PROMPT]   Total size: {len(prompt_context)} characters")
                print(f"[PROMPT]   First 500 chars:")
                print(f"[PROMPT] {'-' * 70}")
                for line in prompt_context[:500].split('\n'):
                    print(f"[PROMPT] {line}")
                print(f"[PROMPT] ...")
                print(f"[PROMPT] {'-' * 70}")
            except Exception as e:
                print(f"[PROMPT] Error generating context: {e}")

        else:
            print(f"\n[METADATA] Using legacy format (no rich metadata)")
            libraries = task_info.get('common_libraries', [])
            if libraries:
                print(f"[METADATA]   Common libraries: {', '.join(libraries)}")

    else:
        # No explicit task type - try auto-detection
        detected = detect_task_type(instr_text)
        print(f"\n[TASK TYPE] Auto-detected: ({detected})")
        print(f"[TASK TYPE] (No explicit type hint in instruction)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\nSummary:")
print("  - Instructions with (discord) and (telegram) show rich metadata")
print("  - Instructions with (postgres) show legacy format (no metadata yet)")
print("  - Instructions without explicit type use auto-detection")
print("\nThe compiler will now show these details during actual compilation!")
