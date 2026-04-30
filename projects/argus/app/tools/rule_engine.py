from dataclasses import dataclass
from enum import Enum
from typing import Any


class ViolationType(str, Enum):
    MISSING_FIELD = "MISSING_FIELD"
    BAD_FORMAT = "BAD_FORMAT"
    PRICE_ANOMALY = "PRICE_ANOMALY"
    MISSING_TAXONOMY = "MISSING_TAXONOMY"
    DUPLICATE = "DUPLICATE"


@dataclass
class Violation:
    rule: ViolationType
    field: str
    detail: str
    confidence: float = 1.0


# Fields required for every item regardless of category
_REQUIRED_FIELDS: list[str] = [
    "sku_id",
    "item_name",
    "brand",
    "department",
    "unit_price",
    "allergen_statement",  # FSMA 204 / FDA compliance
]

# Compliance-class fields — violations always require human approval
COMPLIANCE_FIELDS: frozenset[str] = frozenset({"allergen_statement"})

_PRICE_MAX = 500.0  # flag items above this for manual review


def run_rules(
    item: dict[str, Any],
    known_skus: set[str] | None = None,
) -> list[Violation]:
    """Run all deterministic validation rules against an item event.

    Args:
        item: Normalized item event dict (Syndigo schema).
        known_skus: Optional set of already-seen SKU IDs for duplicate detection.

    Returns:
        List of Violation objects. Empty list = clean item.
    """
    violations: list[Violation] = []
    violations.extend(_check_missing_fields(item))
    violations.extend(_check_bad_format(item))
    violations.extend(_check_price_anomaly(item))
    violations.extend(_check_missing_taxonomy(item))
    if known_skus is not None:
        violations.extend(_check_duplicate(item, known_skus))
    return violations


def _check_missing_fields(item: dict[str, Any]) -> list[Violation]:
    violations = []
    for f in _REQUIRED_FIELDS:
        val = item.get(f)
        if val is None or (isinstance(val, str) and not val.strip()):
            violations.append(
                Violation(
                    rule=ViolationType.MISSING_FIELD,
                    field=f,
                    detail=f"Required field '{f}' is absent or empty",
                )
            )
    return violations


def _check_bad_format(item: dict[str, Any]) -> list[Violation]:
    violations = []

    upc = item.get("upc")
    if upc is not None:
        upc_str = str(upc).strip()
        if not upc_str.isdigit() or len(upc_str) != 12:
            violations.append(
                Violation(
                    rule=ViolationType.BAD_FORMAT,
                    field="upc",
                    detail=f"UPC must be exactly 12 digits; got '{upc_str}'",
                )
            )

    gtin = item.get("gtin")
    if gtin is not None:
        gtin_str = str(gtin).strip()
        if not gtin_str.isdigit() or len(gtin_str) != 14:
            violations.append(
                Violation(
                    rule=ViolationType.BAD_FORMAT,
                    field="gtin",
                    detail=f"GTIN must be exactly 14 digits; got '{gtin_str}'",
                )
            )

    return violations


def _check_price_anomaly(item: dict[str, Any]) -> list[Violation]:
    violations = []
    price = item.get("unit_price")
    if price is None:
        return violations  # caught by MISSING_FIELD

    try:
        price_f = float(price)
    except (TypeError, ValueError):
        violations.append(
            Violation(
                rule=ViolationType.PRICE_ANOMALY,
                field="unit_price",
                detail=f"unit_price is not numeric: '{price}'",
            )
        )
        return violations

    if price_f <= 0:
        violations.append(
            Violation(
                rule=ViolationType.PRICE_ANOMALY,
                field="unit_price",
                detail=f"unit_price must be > 0; got {price_f}",
            )
        )
    elif price_f > _PRICE_MAX:
        violations.append(
            Violation(
                rule=ViolationType.PRICE_ANOMALY,
                field="unit_price",
                detail=f"unit_price {price_f} exceeds threshold {_PRICE_MAX}; flag for review",
                confidence=0.75,  # high price is suspicious but not definitive
            )
        )

    return violations


def _check_missing_taxonomy(item: dict[str, Any]) -> list[Violation]:
    violations = []
    for f in ("department", "sub_department"):
        val = item.get(f)
        if val is None or (isinstance(val, str) and not val.strip()):
            violations.append(
                Violation(
                    rule=ViolationType.MISSING_TAXONOMY,
                    field=f,
                    detail=f"Taxonomy field '{f}' is absent or empty",
                )
            )
    return violations


def _check_duplicate(item: dict[str, Any], known_skus: set[str]) -> list[Violation]:
    sku_id = str(item.get("sku_id", "")).strip()
    if sku_id and sku_id in known_skus:
        return [
            Violation(
                rule=ViolationType.DUPLICATE,
                field="sku_id",
                detail=f"sku_id '{sku_id}' already exists in catalog",
            )
        ]
    return []
