
from src.profiling.profile import detect_semantic_type


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
