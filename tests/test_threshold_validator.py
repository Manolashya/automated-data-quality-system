import pytest

from src.utils.threshold_validator import validate_quality_thresholds


@pytest.fixture
def valid_config():
    return {
        "quality_thresholds": {
            "minimum_overall_score": 80.0,
            "maximum_missing_percentage": 5.0,
            "maximum_duplicate_percentage": 2.0,
        }
    }


def test_valid_thresholds_are_accepted(valid_config):
    result = validate_quality_thresholds(valid_config)

    assert result["minimum_overall_score"] == 80.0
    assert result["maximum_missing_percentage"] == 5.0
    assert result["maximum_duplicate_percentage"] == 2.0


def test_invalid_config_type_is_rejected():
    with pytest.raises(ValueError, match="dictionary"):
        validate_quality_thresholds("invalid")


def test_missing_threshold_section_is_rejected():
    with pytest.raises(ValueError, match="quality_thresholds"):
        validate_quality_thresholds({})


def test_missing_threshold_is_rejected(valid_config):
    del valid_config["quality_thresholds"]["minimum_overall_score"]

    with pytest.raises(ValueError, match="Missing quality threshold"):
        validate_quality_thresholds(valid_config)


@pytest.mark.parametrize("value", ["invalid", True, None])
def test_non_numeric_threshold_is_rejected(valid_config, value):
    valid_config["quality_thresholds"]["minimum_overall_score"] = value

    with pytest.raises(ValueError, match="numeric"):
        validate_quality_thresholds(valid_config)


@pytest.mark.parametrize("value", [-1, 101])
def test_out_of_range_threshold_is_rejected(valid_config, value):
    valid_config["quality_thresholds"]["minimum_overall_score"] = value

    with pytest.raises(ValueError, match="between 0 and 100"):
        validate_quality_thresholds(valid_config)