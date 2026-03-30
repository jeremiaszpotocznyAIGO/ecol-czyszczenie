import json
import os
import textwrap
from pathlib import Path
import random

import pandas as pd
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings


DF_PATH = "mismatches/all_rows_merged.csv"
BASELINE_PATH = "mismatches/baseline_parsed_samples_all.json"
SCORE_PATH = "parser_score.json"


def load_dataframe(df_path: str) -> pd.DataFrame:
    return pd.read_csv(df_path)


def load_json(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, json_path: str) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_existing_scores(score_path: str) -> dict:
    path = Path(score_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def get_lab_with_interpretation(lab_number, parser_baseline, df):
    lab_number = str(lab_number)

    if lab_number not in parser_baseline:
        return None

    row = df.loc[df["Lab_Number"].astype(str) == lab_number]
    if row.empty:
        return None

    row = row.iloc[0]

    result = dict(parser_baseline[lab_number])
    result["Overall_Interpretation"] = row["Overall_Interpretation"]
    result["Overall_Assessment"] = row["Overall_Assessment_pred_file"]

    return result


def get_random_lab_with_max_keys(parser_baseline: dict, max_keys: int = 0) -> str | None:
    eligible = [
        lab_number
        for lab_number, value in parser_baseline.items()
        if isinstance(value, dict) and len(value) <= max_keys
    ]

    if not eligible:
        return None

    return random.choice(eligible)


def has_real_error(scores: dict, lab_number: str) -> bool:
    error = scores.get(str(lab_number), {}).get("error", "")
    if error is None:
        return False
    error = str(error).strip()
    return bool(error) and error.lower() != "none"


def get_next_error_index(ordered_labs: list[str], scores: dict, current_idx: int) -> int | None:
    for i in range(current_idx + 1, len(ordered_labs)):
        if has_real_error(scores, ordered_labs[i]):
            return i
    return None


def print_lab_data(lab_number: str, lab_data: dict, idx: int, total: int, width: int = 100) -> None:
    print("=" * width)
    print(f"[{idx + 1}/{total}] Lab_Number: {lab_number}")
    print("=" * width)

    for key, value in lab_data.items():
        if pd.isna(value):
            value = ""

        if key == "Overall_Interpretation":
            print(f"{key}:")
            wrapped = textwrap.fill(
                str(value),
                width=width,
                initial_indent="  ",
                subsequent_indent="  ",
            )
            print(wrapped)
        else:
            print(f"{key}: {value}")

    print("=" * width)
    print(
        "Enter = save and next | Ctrl+N = next | Ctrl+P = previous | "
        "Ctrl+R = random | Ctrl+E = next with error | Ctrl+Q = quit"
    )
    print()


def get_ordered_lab_numbers(df: pd.DataFrame, parser_baseline: dict) -> list[str]:
    labs = []
    seen = set()

    for lab in df["Lab_Number"].astype(str):
        if lab in parser_baseline and lab not in seen:
            labs.append(lab)
            seen.add(lab)

    return labs


def build_session():
    kb = KeyBindings()
    session = PromptSession()

    @kb.add("c-n")
    def _(event):
        event.app.exit(result=("next", event.app.current_buffer.text))

    @kb.add("c-p")
    def _(event):
        event.app.exit(result=("prev", event.app.current_buffer.text))

    @kb.add("c-r")
    def _(event):
        event.app.exit(result=("random", event.app.current_buffer.text))

    @kb.add("c-e")
    def _(event):
        event.app.exit(result=("next_error", event.app.current_buffer.text))

    @kb.add("c-q")
    def _(event):
        event.app.exit(result=("quit", event.app.current_buffer.text))

    return session, kb


def prompt_error(session: PromptSession, kb: KeyBindings, existing_text: str) -> tuple[str, str]:
    result = session.prompt(
        "error: ",
        default=existing_text,
        key_bindings=kb,
    )

    # If user presses Enter normally, prompt returns plain text.
    if isinstance(result, str):
        return "next", result

    # If user pressed a custom shortcut, we get the tuple from event.app.exit(...)
    return result


def main():
    df = load_dataframe(DF_PATH)
    parser_baseline = load_json(BASELINE_PATH)
    scores = load_existing_scores(SCORE_PATH)

    ordered_labs = get_ordered_lab_numbers(df, parser_baseline)
    total = len(ordered_labs)

    if total == 0:
        print("No matching Lab_Number values found.")
        return

    session, kb = build_session()
    idx = 0

    while 0 <= idx < total:
        lab_number = ordered_labs[idx]
        lab_data = get_lab_with_interpretation(lab_number, parser_baseline, df)

        if lab_data is None:
            idx += 1
            continue

        existing_error = scores.get(lab_number, {}).get("error", "")

        clear_terminal()
        print_lab_data(lab_number, lab_data, idx, total)

        try:
            action, error_text = prompt_error(session, kb, existing_error)
        except KeyboardInterrupt:
            save_json(scores, SCORE_PATH)
            clear_terminal()
            print(f"Stopped. Progress saved to {SCORE_PATH}")
            return

        if error_text.strip():
            scores[lab_number] = {"error": error_text}
        else:
            scores.pop(lab_number, None)

        save_json(scores, SCORE_PATH)

        if action == "next":
            if idx < total - 1:
                idx += 1
            else:
                clear_terminal()
                print(f"Done. All progress saved to {SCORE_PATH}")
                return

        elif action == "prev":
            if idx > 0:
                idx -= 1

        elif action == "random":
            random_lab = get_random_lab_with_max_keys(parser_baseline, max_keys=0)
            if random_lab is not None and random_lab in ordered_labs:
                idx = ordered_labs.index(random_lab)

        elif action == "next_error":
            next_error_idx = get_next_error_index(ordered_labs, scores, idx)
            if next_error_idx is not None:
                idx = next_error_idx

        elif action == "quit":
            clear_terminal()
            print(f"Stopped. Progress saved to {SCORE_PATH}")
            return

    clear_terminal()
    print(f"Done. All progress saved to {SCORE_PATH}")


if __name__ == "__main__":
    main()