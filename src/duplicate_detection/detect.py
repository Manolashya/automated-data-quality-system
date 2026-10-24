
import pandas as pd
from rapidfuzz import fuzz


def detect_fuzzy_duplicates(
    df,
    column="Name",
    threshold=85
):
    """
    Identify potentially duplicated records using fuzzy matching.

    Returns a list of dictionaries containing matching row indexes
    and similarity scores. Does not modify or delete records.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if not 0 <= threshold <= 100:
        raise ValueError("Threshold must be between 0 and 100")

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")

    results = []

    values = df[column].tolist()

    for i in range(len(values)):
        if pd.isna(values[i]):
            continue

        value1 = str(values[i]).strip()

        if not value1:
            continue

        for j in range(i + 1, len(values)):
            if pd.isna(values[j]):
                continue

            value2 = str(values[j]).strip()

            if not value2:
                continue

            score = fuzz.ratio(
                value1.casefold(),
                value2.casefold()
            )

            if score >= threshold:
                results.append({
                    "row_1": df.index[i],
                    "row_2": df.index[j],
                    "column": column,
                    "value_1": value1,
                    "value_2": value2,
                    "similarity": round(score, 2)
                })

    return results
