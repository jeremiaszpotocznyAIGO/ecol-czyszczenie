import re


# Wspólne domyślne zbiory
DEFAULT_GLOBAL_KEYS = {"wszystkie_parametry", "oznaczone_parametry", "pozostałe_parametry"}

DEFAULT_GOOD_STATUSES = {
    "w_normie",
    "w_zakresie_typowym",
    "w_zakresie_bezpiecznym",
    "w_dopuszczalnym_zakresie",
    "w_zakresie_dopuszczalnym",
    "w_akceptowalnym_zakresie",
    "w_zakresie_akceptowalnym",
    "w_zakresie_granicznym",
    "brak",
    "brak_wykrycia",
    "nieoznaczone",
    "nieoznaczono",
}

DEFAULT_IGNORE_STATUSES = {"brak_wykrycia", "nieoznaczono"}  # do FN: nie liczymy jako "negatyw"

def iter_param_statuses(sample: dict, ignore_keys=DEFAULT_GLOBAL_KEYS):
    """Zwraca statusy tylko dla kluczy-parametrów (ignoruje globalne)."""
    if not isinstance(sample, dict) or not sample:
        return []
    out = []
    for k, v in sample.items():
        if k in ignore_keys or v is None:
            continue
        out.append(str(v))
    return out


# False negatives
def get_false_negatives(
    data,
    df,
    min_negative_params=2,
    GOOD_STATUSES=DEFAULT_GOOD_STATUSES,
    IGNORE_STATUSES=DEFAULT_IGNORE_STATUSES,
    IGNORE_KEYS=DEFAULT_GLOBAL_KEYS,
    assessment_col="Overall_Assessment_pred_file",
    ok_assessments=(0,),
):
    def negative_count(sample: dict) -> int:
        statuses = iter_param_statuses(sample, ignore_keys=IGNORE_KEYS)
        return sum(
            (s not in GOOD_STATUSES) and (s not in IGNORE_STATUSES)
            for s in statuses
        )

    negative_labs = [str(lab) for lab, sample in data.items() if negative_count(sample) >= min_negative_params]
    ok_labs = df.loc[df[assessment_col].isin(ok_assessments), "Lab_Number"].astype(str).tolist()
    return sorted(set(negative_labs) & set(ok_labs))


# False positives
def get_false_positives(
    data,
    df,
    GOOD_STATUSES=DEFAULT_GOOD_STATUSES,
    GLOBAL_OK_KEYS=DEFAULT_GLOBAL_KEYS,
    assessment_col="Overall_Assessment_pred_file",
    bad_assessments=(1, 2),
    require_any_param=True,
):
    def is_ok_sample(sample: dict) -> bool:
        if not isinstance(sample, dict) or not sample:
            return False

        statuses = iter_param_statuses(sample, ignore_keys=GLOBAL_OK_KEYS)

        # brak parametrów (tylko global OK albo pusto)
        if not statuses:
            if require_any_param:
                return False
            return any(str(sample.get(k)) in GOOD_STATUSES for k in GLOBAL_OK_KEYS)

        return all(s in GOOD_STATUSES for s in statuses)

    ok_labs = [str(lab) for lab, sample in data.items() if is_ok_sample(sample)]
    flagged_labs = df.loc[df[assessment_col].isin(bad_assessments), "Lab_Number"].astype(str).tolist()
    return sorted(set(ok_labs) & set(flagged_labs))


# Potencjal quidelines
def get_potential_guidelines(
    data,
    df,
    assessment_col="Overall_Assessment_pred_file",
    text_col="Overall_Interpretation",
    expected_class=1,
    suspicious_classes=(0, 2),
    # progi
    min_borderline_params=1,      # ile "lekko/granicznie" minimalnie
    min_total_params=3,           # żeby wykluczyć puste/przypadkowe
    ok_to_borderline_ratio=1.0,   # ok_count >= ratio * borderline_count (1.0 = "co najmniej tyle samo OK co borderline")
    require_softening_phrase=False,  # jeśli True -> wymaga frazy typu "jednak mieści się"
    # co ignorujemy
    ignore_keys=("wszystkie_parametry", "oznaczone_parametry", "pozostałe_parametry"),
    ignore_statuses=("brak_wykrycia", "nieoznaczono", "nieoznaczone", "brak"),
):
    """
    Szuka próbek, które wg parsera wyglądają na "borderline" (powinny być klasą 1),
    ale w DF mają klasę 0 albo 2.

    Borderline = brak mocnych alarmów + jest trochę lekko/granicznie + jest też sporo OK.
    Dodatkowo (opcjonalnie) wzmacniamy to frazami z tekstu: "jednak mieści się", "jeszcze w ... zakresie" itd.
    """

    # --- koszyki statusów ---
    OK_STATUSES = {
        "w_normie",
        "w_zakresie_typowym",
        "w_zakresie_bezpiecznym",
        "w_dopuszczalnym_zakresie",
        "w_akceptowalnym_zakresie",
        "w_zakresie_dopuszczalnym",
        "w_zakresie_akceptowalnym",
        "w_zakresie_granicznym",  # często borderline, ale tu liczymy jako OK tylko w proporcjach; realnie wrzucimy do borderline poniżej
    }

    # borderline / lekkie
    BORDERLINE_STATUSES = {
        "w_zakresie_granicznym",
        "lekko_podniesiony",
        "lekko_obniżony",
        "nieznacznie_podniesiony",
        "nieznacznie_obniżony",
        "pogorszony",   # jeśli u Ciebie "pogorszony" to raczej 1; "mocno_pogorszony" jest w mocnych
        "nieznacznie_odbiega",
    }

    # mocne / alarm (wyklucza borderline)
    STRONG_STATUSES = {
        "krytycznie_podniesiony",
        "krytycznie_obniżony",
        "znacznie_podniesiony",
        "znacznie_obniżony",
        "mocno_podwyższony",
        "mocno_obniżony",
        "mocno_pogorszony",
        "powyżej_dopuszczalnego_limitu",
        "poza_dopuszczalnym_zakresem",
        "powyżej_typowego",
        "poniżej_typowego",
        # jeśli chcesz, możesz tu dodać też: "podniesiony", "obniżony"
        # ale na razie zostawiam jako "średnie" (bo bywa semantycznie łagodne w opisach)
    }

    # --- frazy "łagodzące" / borderline ---
    SOFTENING_RE = re.compile(
        r"(?:\bjednak\b|\bale\b|\bpomimo\b|\bmimo\b|\baczkolwiek\b|"
        r"mieści\s+się|wciąż\s+mieści\s+się|jeszcze\s+w\s+(?:dopuszczalnym|akceptowalnym|bezpiecznym)\s+"
        r"(?:zakresie|przedziale)|nie\s+krytycznie|trend\s+stabiln|bez\s+istotnego\s+przyrostu)",
        flags=re.I
    )

    # mapowanie Lab_Number -> (assessment, text) z df
    df_map = {}
    for _, row in df.iterrows():
        lab = str(row["Lab_Number"])
        df_map[lab] = (row.get(assessment_col, None), row.get(text_col, ""))

    def is_borderline(sample: dict, text: str) -> bool:
        if not isinstance(sample, dict) or not sample:
            return False

        ok_cnt = 0
        borderline_cnt = 0
        strong_cnt = 0
        total_cnt = 0

        for k, v in sample.items():
            if k in ignore_keys:
                continue
            if v is None:
                continue

            sv = str(v)

            if sv in ignore_statuses:
                continue

            total_cnt += 1

            if sv in STRONG_STATUSES:
                strong_cnt += 1
                continue

            if sv in BORDERLINE_STATUSES:
                borderline_cnt += 1
                continue

            if sv in OK_STATUSES:
                ok_cnt += 1
                continue

            # wszystko inne traktujemy jako "średnie" -> podbija total, ale nie ok/borderline
            # (np. "podniesiony" / "obniżony" możesz później wrzucić do STRONG, jeśli chcesz ostrzej)
            pass

        if total_cnt < min_total_params:
            return False
        if strong_cnt > 0:
            return False
        if borderline_cnt < min_borderline_params:
            return False
        if ok_cnt < ok_to_borderline_ratio * borderline_cnt:
            return False

        if require_softening_phrase:
            return bool(SOFTENING_RE.search(str(text or "")))

        # jeśli nie wymagamy frazy, to i tak warto ją traktować jako “bonus” (nie jako warunek)
        return True

    out = []
    for lab, sample in data.items():
        lab = str(lab)
        if lab not in df_map:
            continue

        assessment, text = df_map[lab]
        if assessment not in suspicious_classes:
            continue

        if is_borderline(sample, text):
            out.append(lab)

    return sorted(out)

