import json
import pandas as pd

def labs_to_review_json(
    lab_numbers,
    df,
    parsed_data,
    text_col="Overall_Interpretation",
    pred_col="Prediction",
    gt_col="Overall_Assessment_data",
):
    """
    {
      "LAB1": {
        "sample": "...",
        "parser_result": {...},
        "prediction": <pred from df[pred_col]>,
        "ground_true": <gt from df[gt_col]>
      },
      ...
    }
    """
    # one row per Lab_Number (unique)
    tmp = (
        df[["Lab_Number", text_col, pred_col, gt_col]]
        .assign(Lab_Number=df["Lab_Number"].astype(str))
        .drop_duplicates(subset=["Lab_Number"])
        .set_index("Lab_Number")
    )

    out = {}
    for lab in map(str, lab_numbers):
        if lab in tmp.index:
            row = tmp.loc[lab]
            sample = "" if row[text_col] is None else str(row[text_col])
            pred = row[pred_col]
            gt = row[gt_col]
        else:
            sample, pred, gt = "", None, None

        out[lab] = {
            "sample": sample,
            "parser_result": parsed_data.get(lab, {}),
            "prediction": None if pred is None else int(pred) if str(pred).isdigit() else pred,
            "ground_true": None if gt is None else int(gt) if str(gt).isdigit() else gt,
        }

    return out

def labs_to_review_csv(
    lab_numbers,
    df,
    parsed_data,
    text_col="Overall_Interpretation",
    pred_col="Prediction",
    gt_col="Overall_Assessment_data",
):
    """
    Returns a dataframe with columns:
    Lab_Number, sample_description, parser_output, prediction, ground_truth
    """

    tmp = (
        df[["Lab_Number", text_col, pred_col, gt_col]]
        .assign(Lab_Number=df["Lab_Number"].astype(str))
        .drop_duplicates(subset=["Lab_Number"])
        .set_index("Lab_Number")
    )

    rows = []

    for lab in map(str, lab_numbers):

        if lab in tmp.index:
            row = tmp.loc[lab]
            sample = "" if row[text_col] is None else str(row[text_col])
            pred = row[pred_col]
            gt = row[gt_col]
        else:
            sample, pred, gt = "", None, None

        parser_result = parsed_data.get(lab, {})

        rows.append({
            "Lab_Number": lab,
            "sample_description": sample,
            "parser_output": json.dumps(parser_result, ensure_ascii=False),
            "prediction": None if pred is None else int(pred) if str(pred).isdigit() else pred,
            "ground_truth": None if gt is None else int(gt) if str(gt).isdigit() else gt,
        })

    return pd.DataFrame(rows)