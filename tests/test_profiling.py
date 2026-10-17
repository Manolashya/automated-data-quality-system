
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_FILE = PROJECT_ROOT / "src" / "profiling" / "profile.py"


def load_detect_semantic_type():
    """Load the semantic detection function without running the whole script."""
    source = PROFILE_FILE.read_text(encoding="utf-8")
    start = source.index("def detect_semantic_type(column):")
    end = source.index("\n\nfor column in df.columns:", start)

    function_source = source[start:end]
    namespace = {}
    exec(function_source, namespace)

    return namespace["detect_semantic_type"]


detect_semantic_type = load_detect_semantic_type()


def test_detect_email_column():
    assert detect_semantic_type("Email") == "Email"


def test_detect_phone_column():
    assert detect_semantic_type("Phone_Number") == "Phone"


def test_detect_date_column():
    assert detect_semantic_type("Purchase_Date") == "Date"


def test_detect_name_column():
    assert detect_semantic_type("Customer_Name") == "Name"


def test_detect_id_column():
    assert detect_semantic_type("Customer_ID") == "ID"


def test_detect_gender_column():
    assert detect_semantic_type("Gender") == "Categorical"


def test_detect_city_column():
    assert detect_semantic_type("City") == "Categorical"


def test_detect_age_column():
    assert detect_semantic_type("Age") == "Numeric"


def test_detect_income_column():
    assert detect_semantic_type("Income") == "Numeric"


def test_detect_purchase_amount_column():
    assert detect_semantic_type("Purchase_Amount") == "Numeric"


def test_detect_unknown_column():
    assert detect_semantic_type("Favorite_Color") == "Unknown"
