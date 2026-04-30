import pytest
from app.tools.rule_engine import (
    COMPLIANCE_FIELDS,
    Violation,
    ViolationType,
    run_rules,
)


def _base_item(**overrides) -> dict:
    item = {
        "sku_id": "PS-12345",
        "item_name": "Premium Brand Hazelnut Spread",
        "brand": "Premium Brand",
        "department": "GROCERY",
        "sub_department": "NUT BUTTERS",
        "unit_price": 4.99,
        "allergen_statement": "Contains: Tree Nuts (Hazelnut)",
        "upc": "012345678901",
    }
    item.update(overrides)
    return item


def _violations_of_type(violations: list[Violation], rule: ViolationType) -> list[Violation]:
    return [v for v in violations if v.rule == rule]


# ---------------------------------------------------------------------------
# MISSING_FIELD
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_field",
    ["sku_id", "item_name", "brand", "department", "unit_price", "allergen_statement"],
)
def test_missing_field_detected(missing_field):
    item = _base_item()
    item[missing_field] = None
    violations = run_rules(item)
    mf = _violations_of_type(violations, ViolationType.MISSING_FIELD)
    assert any(v.field == missing_field for v in mf)


def test_empty_string_counts_as_missing():
    item = _base_item(allergen_statement="   ")
    violations = run_rules(item)
    mf = _violations_of_type(violations, ViolationType.MISSING_FIELD)
    assert any(v.field == "allergen_statement" for v in mf)


def test_clean_item_has_no_violations():
    assert run_rules(_base_item()) == []


def test_allergen_statement_is_compliance_field():
    assert "allergen_statement" in COMPLIANCE_FIELDS


# ---------------------------------------------------------------------------
# BAD_FORMAT
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "upc",
    ["12345", "abcdefghijkl", "0123456789012"],  # too short, non-numeric, too long
)
def test_bad_upc_format(upc):
    item = _base_item(upc=upc)
    violations = run_rules(item)
    bf = _violations_of_type(violations, ViolationType.BAD_FORMAT)
    assert any(v.field == "upc" for v in bf)


def test_valid_upc_no_violation():
    item = _base_item(upc="012345678901")
    violations = run_rules(item)
    assert not _violations_of_type(violations, ViolationType.BAD_FORMAT)


def test_bad_gtin_format():
    item = _base_item(gtin="123")
    violations = run_rules(item)
    bf = _violations_of_type(violations, ViolationType.BAD_FORMAT)
    assert any(v.field == "gtin" for v in bf)


def test_valid_gtin_no_violation():
    item = _base_item(gtin="01234567890128")
    violations = run_rules(item)
    assert not _violations_of_type(violations, ViolationType.BAD_FORMAT)


# ---------------------------------------------------------------------------
# PRICE_ANOMALY
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("price", [0, -1.0, -0.01])
def test_zero_or_negative_price(price):
    item = _base_item(unit_price=price)
    violations = run_rules(item)
    pa = _violations_of_type(violations, ViolationType.PRICE_ANOMALY)
    assert any(v.field == "unit_price" for v in pa)


def test_price_above_threshold_flagged():
    item = _base_item(unit_price=999.99)
    violations = run_rules(item)
    pa = _violations_of_type(violations, ViolationType.PRICE_ANOMALY)
    assert any(v.field == "unit_price" for v in pa)


def test_price_above_threshold_lower_confidence():
    item = _base_item(unit_price=999.99)
    violations = run_rules(item)
    pa = _violations_of_type(violations, ViolationType.PRICE_ANOMALY)
    high_price = next(v for v in pa if v.field == "unit_price")
    assert high_price.confidence < 1.0


def test_non_numeric_price():
    item = _base_item(unit_price="free")
    violations = run_rules(item)
    pa = _violations_of_type(violations, ViolationType.PRICE_ANOMALY)
    assert any(v.field == "unit_price" for v in pa)


def test_normal_price_no_anomaly():
    item = _base_item(unit_price=4.99)
    violations = run_rules(item)
    assert not _violations_of_type(violations, ViolationType.PRICE_ANOMALY)


# ---------------------------------------------------------------------------
# MISSING_TAXONOMY
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tax_field", ["department", "sub_department"])
def test_missing_taxonomy_field(tax_field):
    item = _base_item()
    item[tax_field] = None
    violations = run_rules(item)
    mt = _violations_of_type(violations, ViolationType.MISSING_TAXONOMY)
    assert any(v.field == tax_field for v in mt)


def test_empty_taxonomy_field():
    item = _base_item(sub_department="")
    violations = run_rules(item)
    mt = _violations_of_type(violations, ViolationType.MISSING_TAXONOMY)
    assert any(v.field == "sub_department" for v in mt)


# ---------------------------------------------------------------------------
# DUPLICATE
# ---------------------------------------------------------------------------


def test_duplicate_sku_detected():
    item = _base_item()
    known = {"PS-12345"}
    violations = run_rules(item, known_skus=known)
    dup = _violations_of_type(violations, ViolationType.DUPLICATE)
    assert any(v.field == "sku_id" for v in dup)


def test_new_sku_not_duplicate():
    item = _base_item()
    known = {"PS-99999"}
    violations = run_rules(item, known_skus=known)
    assert not _violations_of_type(violations, ViolationType.DUPLICATE)


def test_no_known_skus_skips_duplicate_check():
    item = _base_item()
    violations = run_rules(item, known_skus=None)
    assert not _violations_of_type(violations, ViolationType.DUPLICATE)
