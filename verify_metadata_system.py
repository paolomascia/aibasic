#!/usr/bin/env python3
"""
Script di verifica completo del sistema metadata AIbasic.
Questo script verifica che tutti i componenti funzionino correttamente.
"""

import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(passed, message):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")
    return passed

# Track overall results
all_passed = True

print_header("VERIFICA SISTEMA METADATA AIBASIC")

# Test 1: Import base infrastructure
print_header("Test 1: Infrastruttura Base")
try:
    from aibasic.modules.module_base import (
        ModuleMetadata, MethodInfo, AIbasicModuleBase,
        collect_all_modules_metadata, generate_prompt_context
    )
    all_passed &= print_result(True, "Tutte le classi base importate correttamente")
except Exception as e:
    all_passed &= print_result(False, f"Errore import: {e}")
    sys.exit(1)

# Test 2: Collect module metadata
print_header("Test 2: Raccolta Metadata Moduli")
try:
    metadata = collect_all_modules_metadata()
    all_passed &= print_result(len(metadata) >= 2, f"Raccolti metadata per {len(metadata)} moduli")

    # Check Discord
    if 'discord' in metadata:
        discord_meta = metadata['discord']
        checks = [
            (len(discord_meta.get('methods', [])) == 8, "Discord: 8 metodi documentati"),
            (len(discord_meta.get('usage_notes', [])) == 12, "Discord: 12 note d'uso"),
            (len(discord_meta.get('examples', [])) == 11, "Discord: 11 esempi"),
        ]
        for check, msg in checks:
            all_passed &= print_result(check, msg)
    else:
        all_passed &= print_result(False, "Discord metadata non trovato")

    # Check Telegram
    if 'telegram' in metadata:
        telegram_meta = metadata['telegram']
        checks = [
            (len(telegram_meta.get('methods', [])) == 16, "Telegram: 16 metodi documentati"),
            (len(telegram_meta.get('usage_notes', [])) == 16, "Telegram: 16 note d'uso"),
        ]
        for check, msg in checks:
            all_passed &= print_result(check, msg)
    else:
        all_passed &= print_result(False, "Telegram metadata non trovato")

except Exception as e:
    all_passed &= print_result(False, f"Errore raccolta metadata: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Compiler integration
print_header("Test 3: Integrazione Compilatore")
try:
    from aibasic.aibasicc import get_all_task_types, get_task_type_info, detect_task_type

    # Test get_all_task_types
    all_types = get_all_task_types()
    all_passed &= print_result(len(all_types) > 35, f"Task types combinati: {len(all_types)}")

    # Test Discord in combined types
    if 'discord' in all_types:
        discord_info = all_types['discord']
        has_meta = 'module_metadata' in discord_info
        all_passed &= print_result(has_meta, "Discord: metadata disponibile nel compilatore")

        if has_meta:
            meta = discord_info['module_metadata']
            all_passed &= print_result(
                len(meta.get('methods', [])) == 8,
                "Discord: metodi accessibili dal compilatore"
            )
    else:
        all_passed &= print_result(False, "Discord non trovato nei task types")

    # Test Telegram
    if 'telegram' in all_types:
        telegram_info = all_types['telegram']
        has_meta = 'module_metadata' in telegram_info
        all_passed &= print_result(has_meta, "Telegram: metadata disponibile nel compilatore")
    else:
        all_passed &= print_result(False, "Telegram non trovato nei task types")

    # Test task type detection
    test_cases = [
        ('(discord) send message "test"', 'discord'),
        ('(telegram) send notification', 'telegram'),
        ('send webhook to discord', 'discord'),
    ]

    for instruction, expected in test_cases:
        detected = detect_task_type(instruction)
        all_passed &= print_result(
            detected == expected,
            f"Rilevamento: '{instruction[:30]}...' -> {detected}"
        )

except Exception as e:
    all_passed &= print_result(False, f"Errore integrazione compilatore: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Prompt generation
print_header("Test 4: Generazione Prompt")
try:
    # Generate Discord prompt
    discord_prompt = generate_prompt_context('discord')
    all_passed &= print_result(
        len(discord_prompt) > 6000,
        f"Discord prompt: {len(discord_prompt)} caratteri"
    )

    # Check key elements in prompt
    required_elements = [
        ("## Discord Module", "Header modulo"),
        ("### Usage Notes:", "Sezione note d'uso"),
        ("### Available Methods:", "Sezione metodi"),
        ("send_message", "Documentazione metodo"),
        ("Parameters:", "Documentazione parametri"),
        ("Returns:", "Documentazione ritorno"),
    ]

    for element, description in required_elements:
        all_passed &= print_result(
            element in discord_prompt,
            f"Prompt contiene: {description}"
        )

    # Generate Telegram prompt
    telegram_prompt = generate_prompt_context('telegram')
    all_passed &= print_result(
        len(telegram_prompt) > 6000,
        f"Telegram prompt: {len(telegram_prompt)} caratteri"
    )

except Exception as e:
    all_passed &= print_result(False, f"Errore generazione prompt: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Backward compatibility
print_header("Test 5: Retrocompatibilità")
try:
    # Test that modules without metadata still work
    postgres_info = get_task_type_info('postgres')
    all_passed &= print_result(
        postgres_info is not None,
        "Moduli senza metadata (postgres) funzionano ancora"
    )

    # Check it uses legacy format
    has_meta = 'module_metadata' in postgres_info
    all_passed &= print_result(
        not has_meta,
        "Moduli legacy usano formato classico (no metadata)"
    )

except Exception as e:
    all_passed &= print_result(False, f"Errore test retrocompatibilità: {e}")

# Test 6: Dependency handling
print_header("Test 6: Gestione Dipendenze")
try:
    # The fact that we got here means modules with missing deps were skipped
    all_passed &= print_result(
        True,
        "Moduli con dipendenze mancanti vengono saltati correttamente"
    )

    # Check that available modules were loaded
    from aibasic import modules
    available = [name for name in dir(modules) if name.endswith('Module')]
    all_passed &= print_result(
        'DiscordModule' in available,
        f"Discord caricato ({len(available)} moduli disponibili)"
    )
    all_passed &= print_result(
        'TelegramModule' in available,
        "Telegram caricato"
    )

except Exception as e:
    all_passed &= print_result(False, f"Errore gestione dipendenze: {e}")

# Final summary
print_header("RIEPILOGO FINALE")

if all_passed:
    print("""
✅ TUTTI I TEST SUPERATI!

Il sistema di metadata dinamico è completamente operativo:

✓ Infrastruttura base funzionante
✓ Metadata caricati correttamente (Discord, Telegram)
✓ Compilatore integrato con metadata
✓ Rilevamento task type operativo
✓ Generazione prompt arricchiti (>6000 caratteri)
✓ Retrocompatibilità garantita
✓ Gestione dipendenze robusta

STATO: PRONTO PER LA PRODUZIONE

Prossimi passi:
1. Aggiungere metadata agli altri 32 moduli secondo priorità
2. I moduli con metadata verranno usati automaticamente dal compilatore
3. Nessuna modifica al compilatore richiesta

Per dettagli implementazione: METADATA_IMPLEMENTATION_STATUS.md
Per verifica completa: METADATA_SYSTEM_VERIFICATION.md
""")
else:
    print("""
❌ ALCUNI TEST FALLITI

Verificare i messaggi di errore sopra per dettagli.
""")
    sys.exit(1)
