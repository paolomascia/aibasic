#!/usr/bin/env python3
"""
Test script to verify the directive prompt for module usage.
Shows how the prompt now explicitly instructs the LLM to use module methods.
"""

import sys
from pathlib import Path
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aibasic.aibasicc import get_task_type_info
from aibasic.modules.module_base import generate_prompt_context

print("=" * 80)
print("TEST: Directive Prompt for Module Usage")
print("=" * 80)

# Test Discord instruction
instruction_text = 'send message "Hello World"'
task_type = 'discord'

print(f"\nInstruction: ({task_type}) {instruction_text}")
print("-" * 80)

# Get task info
task_info = get_task_type_info(task_type)

if 'module_metadata' in task_info:
    module_doc = task_info['module_metadata']
    metadata = module_doc.get('metadata', {})
    module_name = metadata.get('name', 'Unknown')
    task_type_name = metadata.get('task_type', task_type)

    print(f"\n[INFO] Module detected: {module_name}")
    print(f"[INFO] Task type: {task_type_name}")
    print(f"[INFO] Methods available: {len(module_doc.get('methods', []))}")

    # Generate the module context
    module_info = "\n" + generate_prompt_context(task_type) + "\n"

    # Build the critical requirements section (same as in compiler)
    requirements = "\n" + "=" * 70 + "\n"
    requirements += "CRITICAL MODULE USAGE REQUIREMENTS:\n"
    requirements += "=" * 70 + "\n"
    requirements += f"1. MANDATORY: Import and use the {module_name}Module class\n"
    requirements += f"   from aibasic.modules import {module_name}Module\n\n"
    requirements += f"2. MANDATORY: Create module instance (use existing if in context):\n"
    requirements += f"   {task_type_name} = {module_name}Module()\n\n"
    requirements += f"3. MANDATORY: Call the appropriate method from the module\n"
    requirements += f"   - DO NOT write custom code to implement the functionality\n"
    requirements += f"   - DO NOT use external libraries directly (requests, discord.py, etc.)\n"
    requirements += f"   - MUST use the module's pre-defined methods documented above\n\n"
    requirements += f"4. MANDATORY: Follow the exact method signatures shown in documentation\n"
    requirements += f"   - Use the parameter names exactly as documented\n"
    requirements += f"   - Pass parameters in the correct format (dict, string, int, etc.)\n\n"
    requirements += f"5. Example pattern (adapt to the specific instruction):\n"
    requirements += f"   # Import module\n"
    requirements += f"   from aibasic.modules import {module_name}Module\n"
    requirements += f"   # Get or create instance\n"
    requirements += f"   {task_type_name} = {module_name}Module()\n"
    requirements += f"   # Call appropriate method\n"
    requirements += f"   result = {task_type_name}.method_name(param1, param2, ...)\n\n"
    requirements += "6. FORBIDDEN:\n"
    requirements += "   - DO NOT implement webhook calls directly\n"
    requirements += "   - DO NOT use requests.post() or similar\n"
    requirements += "   - DO NOT create custom HTTP clients\n"
    requirements += "   - DO NOT reimplement module functionality\n\n"
    requirements += "7. The module methods are ALREADY IMPLEMENTED and TESTED\n"
    requirements += "   - Simply call them with correct parameters\n"
    requirements += "   - Trust the module to handle the implementation details\n\n"
    requirements += f"8. For THIS specific instruction: '{instruction_text}'\n"
    requirements += f"   YOU MUST:\n"
    requirements += f"   a) Check if '{task_type_name}' is already in context variables\n"
    requirements += f"   b) If not, create it: {task_type_name} = {module_name}Module()\n"
    requirements += f"   c) Identify which method matches the instruction (refer to methods list above)\n"
    requirements += f"   d) Call that method: result = {task_type_name}.method_name(...)\n"
    requirements += f"   e) Store result appropriately\n\n"
    requirements += "   CORRECT EXAMPLE:\n"
    requirements += f"   ```python\n"
    requirements += f"   from aibasic.modules import {module_name}Module\n"
    requirements += f"   {task_type_name} = {module_name}Module()\n"
    requirements += f"   result = {task_type_name}.appropriate_method('param1', param2=value)\n"
    requirements += f"   ```\n\n"
    requirements += "   WRONG EXAMPLE (DO NOT DO THIS):\n"
    requirements += "   ```python\n"
    requirements += "   import requests\n"
    requirements += "   response = requests.post(url, json=data)  # WRONG!\n"
    requirements += "   ```\n"
    requirements += "=" * 70 + "\n\n"

    print("\n" + "=" * 80)
    print("CRITICAL MODULE USAGE REQUIREMENTS (sent to LLM)")
    print("=" * 80)
    print(requirements)

    print("\n" + "=" * 80)
    print("KEY DIFFERENCES FROM BEFORE")
    print("=" * 80)
    print("""
BEFORE (weak instructions):
- "Use the module's methods as documented above"
- "Follow the parameter names and types"
→ LLM often ignored this and generated custom code

AFTER (strong, directive instructions):
✓ "MANDATORY: Import and use the DiscordModule class"
✓ "DO NOT write custom code to implement the functionality"
✓ "DO NOT use external libraries directly (requests, discord.py, etc.)"
✓ "MUST use the module's pre-defined methods"
✓ "FORBIDDEN: DO NOT implement webhook calls directly"
✓ Concrete CORRECT and WRONG examples
✓ Step-by-step instructions for THIS specific instruction
→ LLM should now use the module methods

EXPECTED GENERATED CODE:
```python
from aibasic.modules import DiscordModule
discord = DiscordModule()
result = discord.send_message("Hello World")
```

NOT THIS (what it was generating before):
```python
import requests
webhook_url = "..."
response = requests.post(webhook_url, json={"content": "Hello World"})
```
""")

    print("\n" + "=" * 80)
    print("FULL PROMPT SIZE")
    print("=" * 80)
    print(f"Module documentation: {len(module_info)} characters")
    print(f"Critical requirements: {len(requirements)} characters")
    print(f"Total directive content: {len(module_info) + len(requirements)} characters")

    print("\n" + "=" * 80)
    print("WHY THIS SHOULD WORK BETTER")
    print("=" * 80)
    print("""
1. EXPLICIT FORBIDDEN BEHAVIORS
   - Lists exactly what NOT to do
   - Mentions specific anti-patterns (requests.post, custom HTTP)

2. MANDATORY KEYWORDS
   - Uses "MANDATORY", "MUST", "FORBIDDEN"
   - Creates stronger semantic weight for the LLM

3. CONCRETE EXAMPLES
   - Shows CORRECT code pattern
   - Shows WRONG code pattern
   - Reduces ambiguity

4. STEP-BY-STEP FOR THIS INSTRUCTION
   - Tells LLM exactly what to do for the current instruction
   - References the specific methods list above

5. REPETITION OF KEY CONCEPTS
   - Repeated multiple times in different phrasings
   - "DO NOT reimplement", "use pre-defined methods", etc.

6. VISUAL SEPARATION
   - === borders make it stand out
   - Numbered requirements are easy to follow
""")

else:
    print("\n[WARN] No module metadata found for this task type")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
Il prompt è ora MOLTO PIÙ DIRETTIVO e specifico.
L'LLM dovrebbe ora utilizzare i metodi del modulo invece di
generare codice da zero.

Per testare con il compilatore reale:
  python src/aibasic/aibasicc.py -c aibasic.conf -i test.aib -o output.py

Controlla che il codice generato contenga:
  ✓ from aibasic.modules import DiscordModule
  ✓ discord = DiscordModule()
  ✓ discord.send_message(...)

E NON contenga:
  ✗ import requests
  ✗ requests.post(...)
""")
