def validate_quality_thresholds(config):
    """
    Validate quality threshold configuration values.

    Args:
        config: Dictionary containing quality thresholds.

    Returns:
        Validated threshold dictionary.

    Raises:
        ValueError: If any threshold is missing or invalid.
    """

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary.")

    thresholds = config.get("quality_thresholds")

    if not isinstance(thresholds, dict):
        raise ValueError(
            "Missing or invalid quality_thresholds section."
        )

    required_thresholds = [
        "minimum_overall_score",
        "maximum_missing_percentage",
        "maximum_duplicate_percentage",
    ]

    for key in required_thresholds:

        if key not in thresholds:
            raise ValueError(
                f"Missing quality threshold: {key}"
            )

        value = thresholds[key]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            raise ValueError(
                f"{key} must be a numeric value."
            )

        if not 0 <= value <= 100:
            raise ValueError(
                f"{key} must be between 0 and 100."
            )

    return thresholds