"""Unit tests for validate_item_rules tool — pure Python, no LLM."""
import json

import pytest

from app.agents.item_validator import validate_item_rules


def _item(**overrides: object) -> dict:
    base: dict = {
        "sku_id": "SKU-0042",
        "item_name": "Premium Brand Hazelnut Spread",
        "brand": "Premium Brand",
        "department": "Pantry",
        "sub_department": "Nut Butters & Spreads",
        "unit_price": 5.99,
        "allergen_statement": "Contains: hazelnuts, milk",
        "upc": "012345678901",
    }
    base.update(overrides)
    return base


def _parse(item: dict) -> list[dict]:
    return json.loads(validate_item_rules(json.dumps(item)))


# --- clean item ---

def test_clean_item_no_violations():
    assert _parse(_item()) == []


# --- MISSING_FIELD ---

def test_missing_allergen_statement():
    result = _parse(_item(allergen_statement=None))
    allergen = [v for v in result if v["field"] == "allergen_statement"]
    assert len(allergen) == 1
    assert allergen[0]["rule"] == "MISSING_FIELD"
    assert allergen[0]["confidence"] == 1.0


def test_empty_string_allergen_is_missing():
    result = _parse(_item(allergen_statement="   "))
    assert any(v["field"] == "allergen_statement" for v in result)


def test_missing_item_name():
    result = _parse(_item(item_name=None))
    assert any(v["rule"] == "MISSING_FIELD" and v["field"] == "item_name" for v in result)


# --- BAD_FORMAT ---

def test_bad_upc_non_numeric():
    result = _parse(_item(upc="ABC123456789"))
    bad = [v for v in result if v["rule"] == "BAD_FORMAT" and v["field"] == "upc"]
    assert len(bad) == 1


def test_bad_upc_wrong_length():
    result = _parse(_item(upc="123"))
    assert any(v["rule"] == "BAD_FORMAT" and v["field"] == "upc" for v in result)


def test_bad_gtin_wrong_length():
    result = _parse(_item(gtin="1234"))
    assert any(v["rule"] == "BAD_FORMAT" and v["field"] == "gtin" for v in result)


def test_no_upc_no_bad_format_violation():
    result = _parse(_item())  # no upc key — no violation
    assert not any(v["rule"] == "BAD_FORMAT" for v in result)


# --- PRICE_ANOMALY ---

def test_zero_price():
    result = _parse(_item(unit_price=0))
    assert any(v["rule"] == "PRICE_ANOMALY" for v in result)


def test_negative_price():
    result = _parse(_item(unit_price=-1.0))
    assert any(v["rule"] == "PRICE_ANOMALY" for v in result)


def test_high_price_confidence_reduced():
    result = _parse(_item(unit_price=999.99))
    price_v = [v for v in result if v["rule"] == "PRICE_ANOMALY"]
    assert len(price_v) == 1
    assert price_v[0]["confidence"] == pytest.approx(0.75)


def test_non_numeric_price():
    result = _parse(_item(unit_price="free"))
    assert any(v["rule"] == "PRICE_ANOMALY" for v in result)


# --- MISSING_TAXONOMY ---

def test_missing_department():
    result = _parse(_item(department=None))
    assert any(v["rule"] == "MISSING_TAXONOMY" and v["field"] == "department" for v in result)


def test_missing_sub_department():
    result = _parse(_item(sub_department=None))
    assert any(v["rule"] == "MISSING_TAXONOMY" and v["field"] == "sub_department" for v in result)


# --- Done criterion: 3 violation types in one item ---

def test_three_violation_types_simultaneously():
    item = _item(
        allergen_statement=None,  # MISSING_FIELD
        upc="BAD",                # BAD_FORMAT
        unit_price=999.99,        # PRICE_ANOMALY
    )
    result = _parse(item)
    rule_types = {v["rule"] for v in result}
    assert len(rule_types) >= 3
    assert "MISSING_FIELD" in rule_types
    assert "BAD_FORMAT" in rule_types
    assert "PRICE_ANOMALY" in rule_types


# --- output schema ---

def test_output_is_valid_json_list():
    raw = validate_item_rules(json.dumps(_item(allergen_statement=None)))
    parsed = json.loads(raw)
    assert isinstance(parsed, list)
    assert all({"rule", "field", "detail", "confidence"} <= v.keys() for v in parsed)
