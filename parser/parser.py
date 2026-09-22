# Komentarze dzielą się na kilka dużych grup:
# angielskie i polskie -> narazie analizujemy tylko polskie
# zawierające (lub nie) dopisek "zalecenia i wnioski":
#   klasa CommentSections dzieli opis na część "diagnostyczną" oraz część "zalecenia i wnioski"
#   klasa DiagnosisParser analizuje część diagnostyczną. Dla opisu próbki zwraca słownik {cecha1: natężenie1, cecha2: natężenie2}
#   TODO: poprawić i rozszerzyć parser
#
#   TODO: klasa RecommendationsParser analizuje część z zaleceniami (narazie analizuje tylko jej obecność -> jest sporo opisów "w normie" które są oznaczane jako guideline)
#   
#   Klasą nadrzędną jest OilCommentParser która wywołuje 3 poprzednie po koleji

# parser.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import json
import pandas as pd


from parser.patterns import (
    PARAM_PATTERNS,
    AUX,
    STATUS_RULES,
    STATUS_KIND,
    STATUS_SCORE,
    NEGATION_WHITELIST,
)
from parser.utils import (
    safe_text,
    normalize_text,
    compile_regex_map,
    compile_rules,
    warn_on_duplicate_status_rules,
)

# (opcjonalnie) ostrzeżenia o duplikatach w statusach
warn_on_duplicate_status_rules(STATUS_RULES)

# --- kompilacje regexów ---
PARAM_RE = compile_regex_map(PARAM_PATTERNS, flags=re.I)
STATUS_RE = compile_rules(STATUS_RULES, flags=re.I)
AUX_RE = compile_regex_map(AUX, flags=re.I)

# --- splitowanie klauzul ---
CLAUSE_SPLIT = r"[.\n;]+"
SOFT_SPLIT_ON_COMMA_IF = re.compile(r",\s*(?=(?:%s))" % AUX["MEASURE_LEADS"], re.I)


# Segmentacja: diagnoza vs zalecenia
@dataclass
class CommentSections:
    diagnosis: str
    recommendations: str
    cut_found: bool
    cut_header: Optional[str]


class CommentSegmenter:
    """
    Segmentuje komentarz na część diagnostyczną i część zaleceń/wniosków.
    To jest jedyne miejsce, gdzie 'ucinasz' tekst.
    """
    def __init__(self) -> None:
        # korzysta z konfiguracji z patterns.AUX
        # (jeśli nie ma, fallback na Twoje dotychczasowe nagłówki)
        pat = AUX.get("SECTION_CUT_HEADERS") or r"\b(?:wnioski\s+i\s+zalecenia|zalecenia\s+i\s+wnioski)\b"
        self._cut_re = re.compile(pat, re.I)

    def split(self, text: str) -> CommentSections:
        m = self._cut_re.search(text)
        if not m:
            return CommentSections(
                diagnosis=text.strip(),
                recommendations="",
                cut_found=False,
                cut_header=None,
            )
        return CommentSections(
            diagnosis=text[: m.start()].strip(),
            recommendations=text[m.end() :].strip(),
            cut_found=True,
            cut_header=m.group(0).strip().lower(),
        )


# Pomocnicze: wybór statusu
def apply_status(current: Optional[str], new: Optional[str]) -> str:
    """
    Zasady:
    1) magnitude wygrywa nad range (dla tego samego parametru)
    2) w innych przypadkach wygrywa większy STATUS_SCORE
    """
    if not current:
        return new or ""
    if not new:
        return current

    cur_kind = STATUS_KIND.get(current, "other")
    new_kind = STATUS_KIND.get(new, "other")

    if cur_kind == "range" and new_kind == "magnitude":
        return new
    if cur_kind == "magnitude" and new_kind == "range":
        return current

    if STATUS_SCORE.get(new, 0) > STATUS_SCORE.get(current, 0):
        return new
    return current


def split_clauses(text: str) -> list[str]:
    """
    DZIELI na klauzule. Nie ucina już sekcji zaleceń — to robi CommentSegmenter.
    """
    t = re.sub(r"\s+", " ", text).strip()
    chunks = [c.strip() for c in re.split(CLAUSE_SPLIT, t) if c.strip()]
    clauses: list[str] = []
    for ch in chunks:
        parts = [p.strip() for p in SOFT_SPLIT_ON_COMMA_IF.split(ch) if p.strip()]
        clauses.extend(parts)
    return clauses



def detect_status(fragment: str) -> Optional[str]:
    s = fragment.lower()
    for name, pat in STATUS_RE:
        if pat.search(s):
            return name
    return None


def find_params(clause: str) -> list[tuple[str, int, int]]:
    cl = clause.lower()
    out: list[tuple[str, int, int]] = []
    for name, pat in PARAM_RE.items():
        m = pat.search(cl)
        if m:
            out.append((name, m.start(), m.end()))
    return out


# Specjalne reguły kontekstowe
def is_aviation_lead_context(clause_lower: str) -> bool:
    # ołów + paliwo lotnicze / "sytuacja normalna"
    if "ołów" not in PARAM_RE:
        return False
    if not PARAM_RE["ołów"].search(clause_lower):
        return False
    return bool(
        AUX_RE["AVIATION_FUEL"].search(clause_lower)
        or AUX_RE["NORMAL_PHRASES"].search(clause_lower)
    )


def remove_aviation_lead_effects(result: dict, clause_lower: str) -> None:
    # lotnictwo: nie interpretuj ołowiu/paliwa jako "zanieczyszczenie w oleju"
    if is_aviation_lead_context(clause_lower):
        result.pop("ołów", None)
        result.pop("paliwo", None)


def handle_no_correlation_negation(clause: str, result: dict) -> None:
    """
    "bez korelacji z obniżeniem lepkości ani temperatury zapłonu"
    => lepkość=w_normie, temperatura_zapłonu=w_normie (jeśli nie mają silniejszego)
    """
    cl = clause.lower()
    if not AUX_RE["NO_CORRELATION"].search(cl):
        return

    m = re.search(
        r"(bez\s+korelacji\s+z|nie\s+wskazuje\s+na)\s+obniżeni\w*\s+(.*)$",
        cl,
    )
    if not m:
        return
    tail = m.group(2)

    if "lepkość" in PARAM_RE and PARAM_RE["lepkość"].search(tail):
        result["lepkość"] = apply_status(result.get("lepkość"), "w_normie")
    if "temperatura_zapłonu" in PARAM_RE and PARAM_RE["temperatura_zapłonu"].search(tail):
        result["temperatura_zapłonu"] = apply_status(result.get("temperatura_zapłonu"), "w_normie")


# Globalne "oznaczone/pozostałe parametry OK"
GLOBAL_OK_TAIL = (
    r"(?:"
    r"w\s+normie"
    r"|w\s+dopuszczalnym"
    r"|w\s+akceptowalnym"
    r"|w\s+swoich\s+normalnych\s+dopuszczalnych\s+przedziałach"
    r"|w\s+swoich\s+normalnych\s+zakresach"
    r"|normaln\w*\s+dopuszczaln\w*\s+przedział\w*"
    r"|normaln\w*\s+zakres\w*"
    r")"
)


def global_ok_status(matched_text: str) -> str:
    s = matched_text.lower()
    if re.search(r"\bw\s+normie\b", s):
        return "w_normie"
    if re.search(r"\bakceptowaln\w*\b", s):
        return "w_akceptowalnym_zakresie"
    if re.search(r"\bdopuszczaln\w*\b", s):
        return "w_dopuszczalnym_zakresie"
    if re.search(r"normaln\w*\s+(zakres\w*|przedział\w*)", s):
        return "w_normie"
    return "w_normie"


# Parser diagnostyczny
class DiagnosisParser:
    def parse(self, text: str) -> dict[str, str]:
        text = normalize_text(safe_text(text))
        if not text:
            return {}

        result: dict[str, str] = {}
        tl = text.lower()

        # 1) pozostałe parametry OK
        m = re.search(
            rf"\bpozostał\w*\b.*?\bparametr\w*\b.*?\b{GLOBAL_OK_TAIL}\b",
            tl,
            flags=re.I,
        )
        if m:
            result["pozostałe_parametry"] = global_ok_status(m.group(0))

        # 2) wszystkie/oznaczone parametry OK
        m = re.search(
            rf"\b(?:wszystkie|oznaczone)\b.*?\bparametr\w*\b.*?\b{GLOBAL_OK_TAIL}\b",
            tl,
            flags=re.I,
        )
        if ("pozostałe_parametry" not in result) and m:
            result["oznaczone_parametry"] = global_ok_status(m.group(0))

        # 3) skrót: "oznaczone parametry/wartości ..."
        m = re.search(
            rf"\boznaczon\w*\s+(?:parametr\w*|wartości)\b.*?\b{GLOBAL_OK_TAIL}\b",
            tl,
            flags=re.I,
        )
        if ("oznaczone_parametry" not in result) and ("pozostałe_parametry" not in result) and m:
            result["oznaczone_parametry"] = global_ok_status(m.group(0))

        clauses = split_clauses(text)

        for clause in clauses:
            cl = clause.lower()

            handle_no_correlation_negation(clause, result)

            found = find_params(clause)
            if not found:
                continue

            clause_status = detect_status(clause)

            # lotniczy kontekst ołowiu: nie dodawaj paliwa
            if is_aviation_lead_context(cl):
                found = [(p, a, b) for (p, a, b) in found if p != "paliwo"]
                if not found:
                    continue

            # CASE: brak_wykrycia -> tylko whitelist
            if clause_status == "brak_wykrycia":
                for param, _, _ in found:
                    if param == "ft_ir":
                        continue
                    if param in NEGATION_WHITELIST:
                        result[param] = apply_status(result.get(param), "brak_wykrycia")
                remove_aviation_lead_effects(result, cl)
                continue

            # CASE: wiele parametrów + jeden status w zdaniu
            if clause_status and len(found) >= 2:
                for param, _, _ in found:
                    if param == "ft_ir":
                        continue
                    st = "w_normie" if clause_status == "w_zakresie_typowym" else clause_status
                    result[param] = apply_status(result.get(param), st)
                remove_aviation_lead_effects(result, cl)
                continue

            # CASE: lokalny status w oknie
            for param, s_idx, e_idx in found:
                if param == "ft_ir":
                    continue

                window = 90
                start = max(0, s_idx - window)
                end = min(len(clause), e_idx + window)
                fragment = clause[start:end]
                local = detect_status(fragment)

                if local == "w_zakresie_typowym":
                    local = "w_normie"
                st_clause = "w_normie" if clause_status == "w_zakresie_typowym" else clause_status

                if local:
                    result[param] = apply_status(result.get(param), local)
                elif st_clause:
                    result[param] = apply_status(result.get(param), st_clause)

            remove_aviation_lead_effects(result, cl)

        # deduplikacja: stałe_ciała_obce vs zanieczyszczenia_stałe
        if "stałe_ciała_obce" in result and "zanieczyszczenia_stałe" in result:
            del result["zanieczyszczenia_stałe"]

        return result


# TODO: Parser zaleceń
class RecommendationsParser:
    def parse(self, text: str) -> dict:
        """
        Na razie nie analizujemy zaleceń — miejsce na przyszłą logikę.
        """
        _ = text  # zachowaj sygnaturę, uniknij lint warningów
        return {}


# Orkiestracja: segmentacja + 2 parsery
class OilCommentParser:
    def __init__(self) -> None:
        self.segmenter = CommentSegmenter()
        self.diagnosis_parser = DiagnosisParser()
        self.reco_parser = RecommendationsParser()

    def parse_full(self, text: str) -> dict:
        text = normalize_text(safe_text(text))
        if not text:
            return {}

        sections = self.segmenter.split(text)

        diagnosis_struct = self.diagnosis_parser.parse(sections.diagnosis)
        reco_struct = self.reco_parser.parse(sections.recommendations)

        return {
            "sections": {
                "diagnosis": sections.diagnosis,
                "recommendations": sections.recommendations,
            },
            "diagnosis": diagnosis_struct,
            "recommendations": reco_struct,
            "meta": {
                "cut_found": sections.cut_found,
                "cut_header": sections.cut_header,
            },
        }

    def parse_flat(self, text: str) -> dict[str, str]:
        """
        zachowuje stare zachowanie parse_comment() -> zwraca tylko diagnozę (bez analizy zaleceń i wniosków)
        """
        full = self.parse_full(text)
        return full.get("diagnosis", {}) if full else {}


# Globalna instancja (żeby nie kompilować regexów / nie tworzyć klas w pętli)
_PARSER = OilCommentParser()

# Publiczne API 
def parse_comment(text: str) -> dict[str, str]:
    """
    Stare API: zwraca tylko diagnostyczne parametry/statusy (bez zaleceń).
    """
    return _PARSER.parse_flat(text)


def parse_comment_full(text: str) -> dict:
    """
    Nowe API: zwraca też podział na sekcje + miejsce na rekomendacje.
    """
    return _PARSER.parse_full(text)


# Endpoint do notatnika "analyze.ipynb"
def df_to_json(df, start: int, end: int) -> dict:
    out = {}
    for i in range(start, end):
        lab = str(df["Lab_Number"][i])
        text = df["Overall_Interpretation"][i]
        out[lab] = parse_comment(text)
    return out



def parser_quantifier(
    parser_output,
    feature_to_pattern,
    status_to_abnormality,
    return_df=True,
    fill_missing=None,
    keep_none=False,
):
    """
    Zamienia wynik parsera:
        {
          "P1300010": {"lepkość": "w_normie", "liczba_zasadowa": "w_zakresie_bezpiecznym"},
          ...
        }

    na:
        {
          "P1300010": {
              "Kinematic_viscosity_at_40C": 0.0,
              "Kinematic_viscosity_at_100C": 0.0,
              "Base_number": 0.0,
              ...
          },
          ...
        }

    Parametry
    ----------
    parser_output : dict | str
        Albo już wczytany dict, albo ścieżka do pliku json.
    feature_to_pattern : dict
        Mapowanie FEATURE_COL -> klucz parsera, np.
        {"Kinematic_viscosity_at_40C": "lepkość", ...}
    status_to_abnormality : dict
        Mapowanie status -> liczba abnormalności, np.
        {"w_normie": 0.0, "lekko_podniesiony": 0.5, ...}
    return_df : bool
        Czy zwrócić również DataFrame.
    fill_missing : float | None
        Wartość do wpisania dla kolumn niewystępujących po mapowaniu.
        Jeśli None, brakujące kolumny nie są dopisywane.
    keep_none : bool
        Jeśli False, statusy mapujące się na None są pomijane.
        Jeśli True, zostają wpisane jako None.

    Zwraca
    -------
    quantified_dict : dict
    quantified_df : pd.DataFrame (jeśli return_df=True)
    """
    # 1) wczytanie jeśli podano ścieżkę
    if isinstance(parser_output, str):
        with open(parser_output, "r", encoding="utf-8") as f:
            parser_output = json.load(f)

    # 2) odwrócenie mapowania:
    #    parser_key -> lista kolumn FEATURE_COLS
    pattern_to_features = {}
    for feature_col, parser_key in feature_to_pattern.items():
        pattern_to_features.setdefault(parser_key, []).append(feature_col)

    quantified = {}

    for sample_id, parsed_params in parser_output.items():
        sample_result = {}

        for parser_key, status in parsed_params.items():
            # jeśli parser zwrócił klucz, którego nie mamy w mapowaniu -> pomijamy
            if parser_key not in pattern_to_features:
                continue

            abnormality = status_to_abnormality.get(status, None)

            # jeśli status nieznany lub celowo None i nie chcemy go trzymać
            if abnormality is None and not keep_none:
                continue

            for feature_col in pattern_to_features[parser_key]:
                sample_result[feature_col] = abnormality

        # opcjonalne wypełnienie braków
        if fill_missing is not None:
            for feature_col in feature_to_pattern.keys():
                sample_result.setdefault(feature_col, fill_missing)

        quantified[sample_id] = sample_result

    if not return_df:
        return quantified

    quantified_df = pd.DataFrame.from_dict(quantified, orient="index")
    quantified_df.index.name = "sample_id"
    quantified_df = quantified_df.sort_index(axis=1)

    return quantified, quantified_df