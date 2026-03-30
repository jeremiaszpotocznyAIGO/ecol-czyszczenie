import json
import textwrap
from pathlib import Path

import pandas as pd


DF_PATH = "mismatches/all_rows_merged.csv"
BASELINE_PATH = "mismatches/baseline_parsed_samples_all.json"
OUTPUT_PATH = "lab_output_dump.txt"
SCORE_PATH = "parser_score.json"


def load_existing_scores(score_path: str) -> dict:
    path = Path(score_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def has_real_error(scores: dict, lab_number: str) -> bool:
    error = scores.get(str(lab_number), {}).get("error", "")
    if error is None:
        return False
    error = str(error).strip()
    return bool(error) and error.lower() != "none"


def load_dataframe(df_path: str) -> pd.DataFrame:
    return pd.read_csv(df_path)


def load_json(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_lab_with_interpretation(lab_number, parser_baseline, df, scores):
    lab_number = str(lab_number)

    if lab_number not in parser_baseline:
        return None

    row = df.loc[df["Lab_Number"].astype(str) == lab_number]
    if row.empty:
        return None

    row = row.iloc[0]

    result = dict(parser_baseline[lab_number])
    result["Overall_Interpretation"] = row.get("Overall_Interpretation", "")
    result["Overall_Assessment"] = row.get("Overall_Assessment_pred_file", "")
    result["Saved_Error"] = scores.get(lab_number, {}).get("error", "")

    return result


def get_ordered_lab_numbers(df: pd.DataFrame, parser_baseline: dict) -> list[str]:
    labs = []
    seen = set()

    for lab in df["Lab_Number"].astype(str):
        if lab in parser_baseline and lab not in seen:
            labs.append(lab)
            seen.add(lab)

    return labs


def format_lab_data(lab_number: str, lab_data: dict, idx: int, total: int, width: int = 100) -> str:
    lines = []
    lines.append("=" * width)
    lines.append(f"[{idx + 1}/{total}] Lab_Number: {lab_number}")
    lines.append("=" * width)

    for key, value in lab_data.items():
        if pd.isna(value):
            value = ""

        if key in {"Overall_Interpretation", "Saved_Error"}:
            lines.append(f"{key}:")
            wrapped = textwrap.fill(
                str(value),
                width=width,
                initial_indent="  ",
                subsequent_indent="  ",
            )
            lines.append(wrapped)
        else:
            lines.append(f"{key}: {value}")

    lines.append("=" * width)
    lines.append("")
    return "\n".join(lines)


def main():
    df = load_dataframe(DF_PATH)
    parser_baseline = load_json(BASELINE_PATH)
    scores = load_existing_scores(SCORE_PATH)

    ordered_labs = get_ordered_lab_numbers(df, parser_baseline)

    filtered_labs = [
        lab_number for lab_number in ordered_labs
        if has_real_error(scores, lab_number)
    ]

    if not filtered_labs:
        print("No labs with real errors found.")
        return

    output_chunks = []
    total = len(filtered_labs)

    for idx, lab_number in enumerate(filtered_labs):
        lab_data = get_lab_with_interpretation(lab_number, parser_baseline, df, scores)
        if lab_data is None:
            continue
        output_chunks.append(format_lab_data(lab_number, lab_data, idx, total))

    output_text = "\n".join(output_chunks)

    output_path = Path(OUTPUT_PATH)
    output_path.write_text(output_text, encoding="utf-8")

    print(f"Saved output for {len(output_chunks)} labs to {output_path}")


if __name__ == "__main__":
    main()