
import numpy as np
import pandas as pd


def _calculate_psi(reference, current, bins=10):
    """Calculate Population Stability Index for numerical data."""

    reference = reference.dropna()
    current = current.dropna()

    if reference.empty or current.empty:
        return None

    # Create bins using the reference dataset.
    edges = np.unique(
        np.quantile(reference, np.linspace(0, 1, bins + 1))
    )

    # Handle constant reference data.
    if len(edges) == 1:
        value = edges[0]
        margin = max(abs(value) * 1e-6, 1e-6)
        edges = np.array([
            -np.inf,
            value - margin,
            value + margin,
            np.inf
        ])
    else:
        edges[0] = -np.inf
        edges[-1] = np.inf

    reference_bins = pd.cut(
        reference, bins=edges, include_lowest=True
    )
    current_bins = pd.cut(
        current, bins=edges, include_lowest=True
    )

    reference_counts = (
        reference_bins.value_counts(sort=False).to_numpy()
    )
    current_counts = (
        current_bins.value_counts(sort=False).to_numpy()
    )

    # Smooth zero proportions to avoid logarithm errors.
    epsilon = 1e-6

    reference_proportions = (
        reference_counts + epsilon
    ) / (len(reference) + epsilon * len(reference_counts))

    current_proportions = (
        current_counts + epsilon
    ) / (len(current) + epsilon * len(current_counts))

    psi = np.sum(
        (current_proportions - reference_proportions)
        * np.log(current_proportions / reference_proportions)
    )

    return float(psi)


def _calculate_tvd(reference, current):
    """Calculate Total Variation Distance for categorical data."""

    if reference.dropna().empty or current.dropna().empty:
        return None

    # Convert missing values into a category.
    reference = reference.astype("object").where(
        reference.notna(), "__MISSING__"
    )
    current = current.astype("object").where(
        current.notna(), "__MISSING__"
    )

    reference_proportions = reference.value_counts(
        normalize=True
    )
    current_proportions = current.value_counts(
        normalize=True
    )

    categories = reference_proportions.index.union(
        current_proportions.index
    )

    reference_proportions = (
        reference_proportions.reindex(categories, fill_value=0)
    )
    current_proportions = (
        current_proportions.reindex(categories, fill_value=0)
    )

    return float(
        0.5 * (reference_proportions - current_proportions)
        .abs()
        .sum()
    )


def detect_data_drift(
    reference_df,
    current_df,
    threshold=0.1,
    bins=10
):
    """
    Compare reference and current datasets.

    Numerical columns use PSI.
    Categorical columns use Total Variation Distance.

    Returns a list of drift reports.
    """

    if not isinstance(reference_df, pd.DataFrame):
        raise TypeError("Reference input must be a DataFrame")

    if not isinstance(current_df, pd.DataFrame):
        raise TypeError("Current input must be a DataFrame")

    if not 0 <= threshold:
        raise ValueError("Threshold must be non-negative")

    if bins < 2:
        raise ValueError("Bins must be at least 2")

    common_columns = reference_df.columns.intersection(
        current_df.columns
    )

    results = []

    for column in common_columns:
        reference = reference_df[column]
        current = current_df[column]

        if (
            pd.api.types.is_numeric_dtype(reference)
            and pd.api.types.is_numeric_dtype(current)
        ):
            score = _calculate_psi(
                reference, current, bins=bins
            )
            method = "PSI"

        else:
            score = _calculate_tvd(reference, current)
            method = "TVD"

        if score is None:
            continue

        results.append({
            "column": column,
            "method": method,
            "drift_score": round(score, 6),
            "drift_detected": score >= threshold
        })

    return results
