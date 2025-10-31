#!/usr/bin/env python3
import argparse
import configparser
import json
import sys
import requests

from pathlib import Path
from textwrap import indent

from aibasic.aibasic_intent import determine_intent, InstructionHint

# ==========================
# CONSTANTS
# ==========================
SYSTEM_PROMPT = (
    '''
    You are an AIBasic-to-Python compiler.
    AIBasic is a simple, natural-language, *numbered* instruction language. Each instruction is independent but is compiled in sequence, and you receive the accumulated context from previous steps.

    Your job is:
    1. Read the current context (a JSON-like description of known variables, last outputs, and their meanings).
    2. Read the current AIBasic instruction (in English, e.g. "read the file customers.csv into a dataframe").
    3. Produce Python code that performs that instruction, using Pandas or standard Python whenever appropriate.
    4. Update the context to tell the compiler what variables now exist, or which variable is the “last output” of this step.
    5. Declare which Python imports are required.

    You MUST respond with a **single valid JSON object** with EXACTLY these keys:
    - "code": string — Python code for this single instruction. Must be runnable in sequence with previous code.
    - "context_updates": object — keys are variable names or meta info (e.g. "df", "last_output"), values are short human-readable descriptions.
    - "needs_imports": array of strings — each string is an import, e.g. "pandas as pd", "os", "json".

    Rules:
    - Do NOT add explanations, introductions, markdown, or prose. JSON ONLY.
    - If the instruction is ambiguous, make a reasonable assumption and state it in the "context_updates".
    - If you cannot do the instruction, return code that raises a clear Exception and explain the reason in "context_updates".
    - Prefer Pandas for CSV/Excel/table-like operations.
    - If the instruction refers to “the dataframe”, assume it refers to the most recent dataframe in context (often stored under "df" or under "last_output").
    - Always set "last_output" in "context_updates" to the most relevant variable produced by this step (e.g. "df").

    Output format example (MUST follow this structure):
    {
    "code": "...",
    "context_updates": { ... },
    "needs_imports": [ ... ]
    }
    '''
)

# ==========================
# UTILITY FUNCTIONS
# ==========================
def load_config(path: Path):
    cfg = configparser.ConfigParser()
    read_files = cfg.read(path)
    if not read_files:
        raise FileNotFoundError(f"Config file not found: {path}")
    section = cfg["llm"]
    return {
        "api_url": section.get("API_URL"),
        "api_token": section.get("API_TOKEN"),
        "api_version": section.get("API_VERSION", "1"),
        "model": section.get("MODEL", "gpt-4o-mini"),
    }

def read_aibasic_file(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    instructions = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        instructions.append(line)
    return instructions

def parse_instruction(line: str):
    """
    Example: '10 read the file customers.csv' → (10, 'read the file customers.csv')
    """
    parts = line.split(maxsplit=1)
    if len(parts) == 1:
        return int(parts[0]), ""
    num_str, text = parts
    return int(num_str), text.strip()

def call_llm(conf: dict, context: dict, instruction_text: str, mock: bool = False):
    """
    Call the LLM and make sure we get a valid JSON back.
    We try once. If the first response is not JSON, we send a repair prompt.
    """
    task_type = detect_task_type(instruction_text)

    if mock:
        # --- Simple mock logic for demo purposes ---
        if "read the file" in instruction_text and ".csv" in instruction_text:
            filename = instruction_text.split("file", 1)[1].strip().split()[0]
            code = f"df = pd.read_csv('{filename}')"
            return {
                "code": code,
                "context_updates": {
                    "df": f"pandas.DataFrame containing data from {filename}",
                    "last_output": "df",
                },
                "needs_imports": ["pandas as pd"],
            }
        else:
            return {
                "code": f"# TODO: implement: {instruction_text!r}",
                "context_updates": {"last_output": None},
                "needs_imports": [],
            }

    headers = {
        "Authorization": f"Bearer {conf['api_token']}",
        "Content-Type": "application/json",
    }

    # --- 1) normal prompt ---
    user_prompt = (
        "You are now compiling ONE AIBasic instruction.\n\n"
        f"Task type (hint): {task_type}\n\n"
        "Current CONTEXT (JSON, cumulative from previous steps):\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        f"AIBasic INSTRUCTION to compile:\n{instruction_text}\n\n"
        "Requirements:\n"
        "- Return ONLY a valid JSON object.\n"
        '- Use the exact keys: "code", "context_updates", "needs_imports".\n'
        '- Always set "last_output" in "context_updates".\n'
        "Return only JSON. Do NOT wrap in markdown.\n"
    )

    payload = {
        "model": conf["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(conf["api_url"], headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"LLM call failed: {resp.status_code} {resp.text}")

    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    # try parse
    parsed = _try_parse_llm_json(content)
    if parsed is not None:
        return _normalize_llm_response(parsed)

    # --- 2) repair attempt ---
    repair_prompt = (
        "Your previous response was NOT valid JSON.\n"
        "You MUST now return the SAME information but as a SINGLE valid JSON object.\n"
        "Use the keys: code, context_updates, needs_imports.\n"
        "Do NOT add explanations. JSON ONLY."
    )

    repair_payload = {
        "model": conf["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": content},
            {"role": "user", "content": repair_prompt},
        ],
    }

    repair_resp = requests.post(conf["api_url"], headers=headers, json=repair_payload, timeout=60)
    if repair_resp.status_code != 200:
        raise RuntimeError(f"LLM repair call failed: {repair_resp.status_code} {repair_resp.text}")

    repair_data = repair_resp.json()
    repair_content = repair_data.get("choices", [{}])[0].get("message", {}).get("content", "")

    parsed = _try_parse_llm_json(repair_content)
    if parsed is None:
        # give up, show original content
        raise RuntimeError(f"LLM did not return valid JSON even after repair.\nOriginal:\n{content}\nRepair:\n{repair_content}")

    return _normalize_llm_response(parsed)

def merge_context(old: dict, updates: dict):
    """Merge new updates into the existing context."""
    new_ctx = dict(old)
    new_ctx.update(updates or {})
    return new_ctx

def detect_task_type(instruction: str) -> str:
    text = instruction.lower()
    if "csv" in text or "read the file" in text or "load the file" in text:
        return "csv"
    if "dataframe" in text or "column" in text or "row" in text:
        return "df"
    if "save" in text or "write" in text or "export" in text:
        return "fs"
    if "sum" in text or "add" in text or "multiply" in text or "average" in text:
        return "math"
    if "call" in text and "api" in text:
        return "rest"
    return "other"

def _try_parse_llm_json(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # try common bad pattern: ```json ... ```
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            # sometimes it's "json\n{...}"
            if text.startswith("json"):
                text = text[len("json"):].strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None
        return None


def _normalize_llm_response(parsed: dict):
    code = parsed.get("code", "")
    ctx = parsed.get("context_updates", {}) or {}
    needs = parsed.get("needs_imports", []) or []
    # always enforce last_output
    if "last_output" not in ctx:
        ctx["last_output"] = None
    return {
        "code": code,
        "context_updates": ctx,
        "needs_imports": needs,
    }


# ==========================
# MAIN LOGIC
# ==========================
def main():
    parser = argparse.ArgumentParser(description="AIBasic → Python compiler")
    parser.add_argument("-c", "--config", required=True, help="path to aibasic.conf")
    parser.add_argument("-i", "--input", required=True, help="AIBasic source file")
    parser.add_argument("-o", "--output", required=True, help="output Python file")
    args = parser.parse_args()

    conf_path = Path(args.config)
    src_path = Path(args.input)
    out_path = Path(args.output)

    try:
        conf = load_config(conf_path)
    except Exception as e:
        print(f"[ERROR] loading config: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        instructions = read_aibasic_file(src_path)
    except Exception as e:
        print(f"[ERROR] reading source: {e}", file=sys.stderr)
        sys.exit(1)

    # Initial context
    context = {
        "description": "Context for AIBasic → Python compilation. Holds variable descriptions and last output.",
        "last_output": None,
        "variables": {}
    }

    generated_codes = []
    collected_imports = set()

    print("=== AIBASIC COMPILER START ===")
    print(f"Config file: {conf_path}")
    print(f"Source file: {src_path}")
    print(f"Output file: {out_path}")
    print()

    parsed_instructions = [parse_instruction(line) for line in instructions]
    parsed_instructions.sort(key=lambda t: t[0])

    for line_num, instr_text in parsed_instructions:
        print(f"\n--- Compiling instruction {line_num} ---")
        print(f"Text: {instr_text}")

        hint = determine_intent(instr_text)
        print("[INTENT]", hint.to_dict())

        result = call_llm(conf, context, instr_text)

        required_keys = ("code", "context_updates", "needs_imports")
        for k in required_keys:
            if k not in result:
                raise RuntimeError(f"LLM result missing key {k}: {result}")

        print("Raw LLM result:")
        print(indent(json.dumps(result, ensure_ascii=False, indent=2), "  "))

        context = merge_context(context, result.get("context_updates", {}))

        # update context['variables']
        updates = result.get("context_updates", {})
        if updates:
            if "variables" not in context or not isinstance(context["variables"], dict):
                context["variables"] = {}
            for k, v in updates.items():
                if k not in ("last_output", "description"):
                    context["variables"][k] = v

        print("Updated context:")
        print(indent(json.dumps(context, ensure_ascii=False, indent=2), "  "))

        code = result.get("code", "")
        if code:
            generated_codes.append(f"# {line_num} {instr_text}\n{code}\n")

        for imp in result.get("needs_imports", []):
            collected_imports.add(imp)

    # Write the output file
    with out_path.open("w", encoding="utf-8") as f:
        if collected_imports:
            for imp in sorted(collected_imports):
                f.write(f"{imp}\n")
            f.write("\n")
        f.write("# === Generated by AIBasic Compiler ===\n\n")
        for code in generated_codes:
            f.write(code)
            if not code.endswith("\n"):
                f.write("\n")

    print("\n=== COMPILATION COMPLETE ===")
    print(f"Generated file: {out_path}")


if __name__ == "__main__":
    main()
