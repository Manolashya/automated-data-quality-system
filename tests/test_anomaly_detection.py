
import pandas as pd
import pytest

from src.anomaly_detection.detect import detect_anomalies


def test_anomaly_detection_returns_expected_columns():
    df = pd.DataFrame({
        "Age": [22, 25, 28, 30, 35, 40],
        "Income": [25000, 30000, 35000, 40000, 45000, 50000],
        "Purchase_Amount": [1000, 1500, 2000, 2500, 3000, 3500]
    })

    result = detect_anomalies(df)

    assert "Anomaly" in result.columns
    assert "Anomaly_Score" in result.columns
    assert len(result) == len(df)


def test_anomaly_labels_are_valid():
    df = pd.DataFrame({
        "Age": [22, 25, 28, 30, 35, 40],
        "Income": [25000, 30000, 35000, 40000, 45000, 50000]
    })

    result = detect_anomalies(df)

    assert set(result["Anomaly"]).issubset({"Normal", "Anomaly"})


def test_anomaly_scores_are_numeric():
    df = pd.DataFrame({
        "Age": [22, 25, 28, 30, 35, 40],
        "Income": [25000, 30000, 35000, 40000, 45000, 50000]
    })

    result = detect_anomalies(df)

    assert pd.api.types.is_numeric_dtype(result["Anomaly_Score"])
    assert result["Anomaly_Score"].notna().all()


def test_missing_values_are_handled():
    df = pd.DataFrame({
        "Age": [22, None, 28, 30, 35, 40],
        "Income": [25000, 30000, None, 40000, 45000, 50000]
    })

    result = detect_anomalies(df)

    assert len(result) == len(df)
    assert result["Anomaly"].notna().all()


def test_original_dataframe_is_not_modified():
    df = pd.DataFrame({
        "Age": [22, 25, 28, 30, 35, 40],
        "Income": [25000, 30000, 35000, 40000, 45000, 50000]
    })

    original = df.copy()

    detect_anomalies(df)

    pd.testing.assert_frame_equal(df, original)


def test_empty_dataframe_raises_error():
    df = pd.DataFrame()

    with pytest.raises(ValueError, match="cannot be empty"):
        detect_anomalies(df)


def test_dataframe_without_numeric_columns_raises_error():
    df = pd.DataFrame({
        "Name": ["A", "B", "C"],
        "City": ["X", "Y", "Z"]
    })

    with pytest.raises(ValueError, match="No numerical columns"):
        detect_anomalies(df)


def test_invalid_contamination_raises_error():
    df = pd.DataFrame({
        "Age": [22, 25, 28, 30]
    })

    with pytest.raises(ValueError, match="Contamination"):
        detect_anomalies(df, contamination=0.5)
