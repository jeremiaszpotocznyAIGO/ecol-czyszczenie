# utils.py
from __future__ import annotations

import math
import re

# optional (parser działa też bez pandas)
try:
    import pandas as pd
except Exception:
    pd = None


def safe_text(x) -> str:
    """
    Zamień None/NaN na pusty string, inaczej rzutuj na str.
    """
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    if pd is not None:
        try:
            if pd.isna(x):
                return ""
        except Exception:
            pass
    return str(x)


def normalize_text(text: str) -> str:
    """
    Normalizacja whitespace:
    - NBSP -> spacja
    - wielokrotne whitespace -> pojedyncza spacja
    - strip
    """
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n+", "\n", text) 
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compile_regex_map(pattern_map: dict[str, str], flags=re.I) -> dict[str, re.Pattern]:
    """
    Kompiluje mapę {name: pattern_str} do {name: re.Pattern}.
    """
    return {k: re.compile(v, flags) for k, v in pattern_map.items()}


def compile_rules(rule_list: list[tuple[str, str]], flags=re.I) -> list[tuple[str, re.Pattern]]:
    """
    Kompiluje listę reguł [(name, pattern_str), ...] do [(name, re.Pattern), ...].
    Zachowuje kolejność (ważne dla priorytetu).
    """
    return [(name, re.compile(pat, flags)) for name, pat in rule_list]


def warn_on_duplicate_status_rules(rules: list[tuple[str, str]]) -> None:
    """
    Pomocniczo: wykryj identyczne pary (status, regex) lub identyczne regexy.
    Nie przerywa działania, tylko ułatwia utrzymanie.
    """
    seen_pair: set[tuple[str, str]] = set()
    seen_pat: dict[str, str] = {}

    for name, pat in rules:
        key = (name, pat)
        if key in seen_pair:
            print(f"[WARN] Duplicate STATUS_RULES entry (same name+regex): {name} -> {pat}")
        seen_pair.add(key)

        if pat in seen_pat and seen_pat[pat] != name:
            print(f"[WARN] Same regex used for different statuses: '{seen_pat[pat]}' and '{name}' -> {pat}")
        else:
            seen_pat[pat] = name