
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def detect_anomalies(
    df,
    contamination=0.05,
    random_state=42
):
    """
    Detect unusual records using Isolation Forest.

    Parameters:
        df: Input pandas DataFrame.
        contamination: Expected proportion of anomalies.
        random_state: Random seed for reproducibility.

    Returns:
        DataFrame containing anomaly labels and scores.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame cannot be empty.")

    if not 0 < contamination < 0.5:
        raise ValueError(
            "Contamination must be greater than 0 and less than 0.5."
        )

    result = df.copy()

    numeric_df = result.select_dtypes(include="number")

    if numeric_df.empty:
        raise ValueError("No numerical columns found.")

    # Remove columns that contain no usable values.
    numeric_df = numeric_df.dropna(axis=1, how="all")

    if numeric_df.empty:
        raise ValueError("No usable numerical columns found.")

    if len(numeric_df) < 2:
        raise ValueError(
            "At least two records are required for anomaly detection."
        )

    # Prepare missing values and train the Isolation Forest model.
    model_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        (
            "model",
            IsolationForest(
                contamination=contamination,
                random_state=random_state
            )
        )
    ])

    model_pipeline.fit(numeric_df)

    # Isolation Forest returns -1 for anomalies and 1 for normal records.
    predictions = model_pipeline.predict(numeric_df)

    # Higher decision scores indicate more normal records.
    scores = model_pipeline.decision_function(numeric_df)

    result["Anomaly_Score"] = scores
    result["Anomaly"] = [
        "Anomaly" if prediction == -1 else "Normal"
        for prediction in predictions
    ]

    return result
