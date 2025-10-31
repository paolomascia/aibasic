"""
aibasic_intent.py

Intent determination for AIBasic natural-language instructions.

Goal:
- Input: "read the file customers.csv into a dataframe"
- Output: InstructionHint(intent="load_csv", filename="customers.csv", target="df", confidence=0.9, ...)

This module is designed to be used *before* the LLM/compiler step.
You can:
1. run rule-based detection (always on)
2. optionally enrich with spaCy (if provided)
3. optionally enrich with semantic similarity / embeddings (if provided)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
import re


# ==========================
# Data model
# ==========================

@dataclass
class InstructionHint:
    intent: str
    confidence: float = 0.5
    filename: Optional[str] = None
    format: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = None
    target: Optional[str] = None
    columns: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)
    raw: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "filename": self.filename,
            "format": self.format,
            "url": self.url,
            "method": self.method,
            "target": self.target,
            "columns": self.columns,
            "extra": self.extra,
            "raw": self.raw,
        }


# Intents we currently support
KNOWN_INTENTS = {
    "load_csv",
    "save_df",
    "df_drop_column",
    "df_rename_column",
    "df_filter",
    "rest_get",
    "math_expr",
    "generic",
}


# ==========================
# Rule-based matchers
# ==========================

def _match_load_csv(text: str, text_low: str) -> Optional[InstructionHint]:
    # Examples this should catch:
    # "read the file customers.csv"
    # "load the file data/customers_2024.csv into a dataframe"
    # "open file sales.csv"
    if any(kw in text_low for kw in ["read the file", "load the file", "open the file", "import from csv", "read csv"]):
        m = re.search(r"file\s+([\w\./\\-]+\.csv)", text, re.IGNORECASE)
        if not m:
            # maybe they said "read customers.csv"
            m = re.search(r"\b([\w\./\\-]+\.csv)\b", text, re.IGNORECASE)
        if m:
            filename = m.group(1)
            # guess target
            target = "df"
            if "into" in text_low:
                # try to get the next word
                mm = re.search(r"into\s+([\w_]+)", text, re.IGNORECASE)
                if mm:
                    target = mm.group(1)
            return InstructionHint(
                intent="load_csv",
                confidence=0.9,
                filename=filename,
                format="csv",
                target=target,
                raw=text,
            )
    return None


def _match_save_df(text: str, text_low: str) -> Optional[InstructionHint]:
    # "save the dataframe to clean.csv"
    # "export the dataframe to out/data.csv"
    if "save the dataframe to" in text_low or "export the dataframe to" in text_low or "write the dataframe to" in text_low:
        m = re.search(r"to\s+([\w\./\\-]+\.\w+)", text, re.IGNORECASE)
        filename = m.group(1) if m else None
        return InstructionHint(
            intent="save_df",
            confidence=0.9 if filename else 0.7,
            filename=filename,
            raw=text,
        )
    return None


def _match_df_drop_column(text: str, text_low: str) -> Optional[InstructionHint]:
    # "remove the column email"
    # "drop column age from the dataframe"
    if "remove the column" in text_low or "drop the column" in text_low or "drop column" in text_low:
        m = re.search(r"column\s+([\w-]+)", text, re.IGNORECASE)
        col = m.group(1) if m else None
        return InstructionHint(
            intent="df_drop_column",
            confidence=0.85 if col else 0.6,
            columns=[col] if col else [],
            raw=text,
        )
    return None


def _match_rest_get(text: str, text_low: str) -> Optional[InstructionHint]:
    # "call the API https://api.example.com/users and save the result in users"
    if "call the api" in text_low or "call api" in text_low or "get from api" in text_low:
        m_url = re.search(r"api\s+(\S+)", text, re.IGNORECASE)
        url = m_url.group(1) if m_url else None
        m_var = re.search(r"save\s+(?:the\s+)?result\s+(?:in|as)\s+(\w+)", text, re.IGNORECASE)
        target = m_var.group(1) if m_var else "response"
        return InstructionHint(
            intent="rest_get",
            confidence=0.9 if url else 0.6,
            url=url,
            method="GET",
            target=target,
            raw=text,
        )
    return None


def _match_math(text: str, text_low: str) -> Optional[InstructionHint]:
    # Simple: "sum 1 2 3", "add 4 and 5", "calculate the average of ..."
    if text_low.startswith("sum ") or text_low.startswith("add "):
        return InstructionHint(
            intent="math_expr",
            confidence=0.7,
            raw=text,
        )
    if "average" in text_low or "mean" in text_low:
        return InstructionHint(
            intent="math_expr",
            confidence=0.6,
            extra={"operation": "average"},
            raw=text,
        )
    return None


RULE_MATCHERS: List[Callable[[str, str], Optional[InstructionHint]]] = [
    _match_load_csv,
    _match_save_df,
    _match_df_drop_column,
    _match_rest_get,
    _match_math,
]


# ==========================
# Optional: semantic / embedding based
# ==========================

DEFAULT_INTENT_TEMPLATES = {
    "load_csv": [
        "read the file <name>.csv",
        "load a csv file",
        "import data from csv",
    ],
    "save_df": [
        "save the dataframe to <path>",
        "export dataframe",
        "write table to csv file",
    ],
    "df_drop_column": [
        "remove the column <col>",
        "drop column <col> from the dataframe",
    ],
    "rest_get": [
        "call the api <url>",
        "get data from http endpoint",
    ],
}


def _cosine_sim(a, b):
    # tiny helper, expects lists of floats
    import math
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _build_template_vectors(embedding_fn) -> Dict[str, List[List[float]]]:
    """
    Pre-encode templates. embedding_fn: str -> List[float]
    """
    index = {}
    for intent, templates in DEFAULT_INTENT_TEMPLATES.items():
        index[intent] = [embedding_fn(t) for t in templates]
    return index


def semantic_intent(
    text: str,
    embedding_fn: Callable[[str], List[float]],
    templates_index: Dict[str, List[List[float]]],
) -> Tuple[str, float]:
    """
    Given a text and a pre-built templates index, return (intent, score).
    """
    vec = embedding_fn(text)
    best_intent = "generic"
    best_score = 0.0
    for intent, tmpl_vecs in templates_index.items():
        score = max(_cosine_sim(vec, tv) for tv in tmpl_vecs)
        if score > best_score:
            best_score = score
            best_intent = intent
    return best_intent, best_score


# ==========================
# Optional: spaCy-based enrichment
# ==========================

def spacy_enrich_hint(text: str, hint: InstructionHint, nlp) -> InstructionHint:
    """
    Enrich an existing hint using spaCy (if available).
    - detect better target after 'into'
    - detect files/urls missed by regex
    - increase confidence if we see clear verb-object structure
    """
    doc = nlp(text)

    # detect URL
    if not hint.url:
        for ent in doc.ents:
            if ent.label_ in ("URL",):
                hint.url = ent.text
                hint.intent = hint.intent or "rest_get"
                hint.confidence = max(hint.confidence, 0.7)

    # detect file-like tokens
    if not hint.filename:
        for token in doc:
            if token.text.endswith(".csv") or token.text.endswith(".json"):
                hint.filename = token.text
                if hint.intent == "generic":
                    hint.intent = "load_csv" if token.text.endswith(".csv") else "load_file"
                hint.confidence = max(hint.confidence, 0.75)

    # detect "into X"
    for i, token in enumerate(doc):
        if token.text.lower() == "into" and i + 1 < len(doc):
            tgt = doc[i + 1].text
            hint.target = hint.target or tgt
            hint.confidence = max(hint.confidence, 0.8)

    return hint


# ==========================
# Public API
# ==========================

def determine_intent(
    text: str,
    *,
    nlp=None,
    embedding_fn: Callable[[str], List[float]] = None,
    templates_index: Dict[str, List[List[float]]] = None,
    semantic_threshold: float = 0.78,
) -> InstructionHint:
    """
    Main entry point.

    1. Try rule-based matchers.
    2. If spaCy pipeline is provided, enrich the result.
    3. If embedding model is provided, try semantic match to refine / override.
    """
    text = text.strip()
    text_low = text.lower()

    # 1) rule-based
    for matcher in RULE_MATCHERS:
        hint = matcher(text, text_low)
        if hint:
            # we already have a decent guess
            if nlp is not None:
                hint = spacy_enrich_hint(text, hint, nlp)
            return hint

    # 2) no rule match → start with generic
    hint = InstructionHint(intent="generic", confidence=0.2, raw=text)

    # 3) spaCy enrich (may find filename/url/etc.)
    if nlp is not None:
        hint = spacy_enrich_hint(text, hint, nlp)

    # 4) semantic refine
    if embedding_fn is not None:
        if templates_index is None:
            templates_index = _build_template_vectors(embedding_fn)
        sem_intent, score = semantic_intent(text, embedding_fn, templates_index)
        if score >= semantic_threshold:
            hint.intent = sem_intent
            hint.confidence = max(hint.confidence, score)

    return hint


# ==========================
# Demo
# ==========================
if __name__ == "__main__":
    tests = [
        "read the file customers.csv into a dataframe",
        "remove the column email from the dataframe",
        "call the API https://api.example.com/users and save the result in users",
        "save the dataframe to out/customers_clean.csv",
        "sum 1 2 3 4 5",
        "filter rows where country = 'IT'",
    ]

    print("=== AIBasic Intent Demo ===")
    for t in tests:
        h = determine_intent(t)
        print(f"\nInstruction: {t}")
        print("Hint:", h.to_dict())
