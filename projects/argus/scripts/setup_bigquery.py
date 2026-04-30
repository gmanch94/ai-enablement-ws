"""BigQuery setup for Argus.

Usage:
  uv run python scripts/setup_bigquery.py            # first-time setup
  uv run python scripts/setup_bigquery.py --overwrite # wipe + re-seed with real embeddings
"""

import argparse
import json
import math
import os
import random
from datetime import datetime, timezone

from google.api_core.exceptions import Conflict
from google.cloud import bigquery

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET = "argus"
TABLE = "correction_history"
EMBEDDING_DIM = 768
SYNTHETIC_RECORDS = 50

SCHEMA = [
    bigquery.SchemaField("record_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("violation_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("field_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("original_value", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("corrected_value", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("brand", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("approved", "BOOL", mode="REQUIRED"),
    bigquery.SchemaField("approval_source", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("approver_email", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField(
        "embedding",
        "FLOAT64",
        mode="REPEATED",
        description="Synthetic unit vector (768-dim). Replace with ML.GENERATE_EMBEDDING before demo.",
    ),
]


def _random_unit_vector(dim: int) -> list[float]:
    """Random unit vector — placeholder until real embeddings are generated."""
    vec = [random.gauss(0, 1) for _ in range(dim)]
    magnitude = math.sqrt(sum(x * x for x in vec))
    return [x / magnitude for x in vec]


def _synthetic_records() -> list[dict]:
    random.seed(42)

    violation_types = [
        ("MISSING_FIELD", "allergen_statement", None, "Contains: Tree Nuts (Hazelnut)", "GROCERY"),
        ("MISSING_FIELD", "allergen_statement", None, "Contains: Milk, Soy", "DAIRY"),
        ("MISSING_FIELD", "allergen_statement", None, "Contains: Wheat", "BAKERY"),
        ("MISSING_FIELD", "unit_price", None, "4.99", "GROCERY"),
        ("MISSING_FIELD", "item_name", None, "Premium Brand Organic Honey", "GROCERY"),
        ("MISSING_FIELD", "brand", None, "Premium Brand", "GROCERY"),
        ("MISSING_FIELD", "department", None, "GROCERY", "GROCERY"),
        ("BAD_FORMAT", "upc", "12345", "012345678901", "GROCERY"),
        ("BAD_FORMAT", "upc", "ABCDE", "012345678902", "FROZEN"),
        ("BAD_FORMAT", "gtin", "123", "01234567890128", "GROCERY"),
        ("PRICE_ANOMALY", "unit_price", "0", "3.49", "PRODUCE"),
        ("PRICE_ANOMALY", "unit_price", "-1.00", "2.99", "DELI"),
        ("PRICE_ANOMALY", "unit_price", "999.99", "9.99", "GROCERY"),
        ("MISSING_TAXONOMY", "sub_department", None, "NUT BUTTERS", "GROCERY"),
        ("MISSING_TAXONOMY", "department", None, "FROZEN", "FROZEN"),
    ]

    categories = ["GROCERY", "FROZEN", "DAIRY", "BAKERY", "PRODUCE", "DELI", "MEAT", "FLORAL"]
    brands = ["Premium Brand", "Organic Brand", "House Brand", "Heritage Brand", "Value Brand"]

    records = []
    for i in range(SYNTHETIC_RECORDS):
        base = violation_types[i % len(violation_types)]
        vtype, field, orig, corrected, cat = base
        approved = random.random() > 0.15  # 85% approval rate

        records.append({
            "record_id": f"syn-{i:04d}",
            "violation_type": vtype,
            "field_name": field,
            "original_value": orig,
            "corrected_value": corrected,
            "category": random.choice(categories),
            "brand": random.choice(brands),
            "approved": approved,
            "approval_source": "HUMAN" if approved else "REJECTED",
            "approver_email": "approver@example.com" if approved else None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "embedding": _random_unit_vector(EMBEDDING_DIM),
        })

    return records


def _real_embedding_records() -> list[dict]:
    """Generate 50 correction history records with real text-embedding-004 vectors."""
    from app.tools.embeddings import generate_embedding

    random.seed(42)

    violation_types = [
        ("MISSING_FIELD", "allergen_statement", None, "Contains: Tree Nuts (Hazelnut)", "GROCERY"),
        ("MISSING_FIELD", "allergen_statement", None, "Contains: Milk, Soy", "DAIRY"),
        ("MISSING_FIELD", "allergen_statement", None, "Contains: Wheat", "BAKERY"),
        ("MISSING_FIELD", "unit_price", None, "4.99", "GROCERY"),
        ("MISSING_FIELD", "item_name", None, "Premium Brand Organic Honey", "GROCERY"),
        ("MISSING_FIELD", "brand", None, "Premium Brand", "GROCERY"),
        ("MISSING_FIELD", "department", None, "GROCERY", "GROCERY"),
        ("BAD_FORMAT", "upc", "12345", "012345678901", "GROCERY"),
        ("BAD_FORMAT", "upc", "ABCDE", "012345678902", "FROZEN"),
        ("BAD_FORMAT", "gtin", "123", "01234567890128", "GROCERY"),
        ("PRICE_ANOMALY", "unit_price", "0", "3.49", "PRODUCE"),
        ("PRICE_ANOMALY", "unit_price", "-1.00", "2.99", "DELI"),
        ("PRICE_ANOMALY", "unit_price", "999.99", "9.99", "GROCERY"),
        ("MISSING_TAXONOMY", "sub_department", None, "NUT BUTTERS", "GROCERY"),
        ("MISSING_TAXONOMY", "department", None, "FROZEN", "FROZEN"),
    ]

    categories = ["GROCERY", "FROZEN", "DAIRY", "BAKERY", "PRODUCE", "DELI", "MEAT", "FLORAL"]
    brands = ["Premium Brand", "Organic Brand", "House Brand", "Heritage Brand", "Value Brand"]

    records = []
    for i in range(SYNTHETIC_RECORDS):
        base = violation_types[i % len(violation_types)]
        vtype, field, orig, corrected, _cat = base
        approved = random.random() > 0.15

        embed_text = f"{vtype}:{field} {corrected or ''}"
        print(f"  [{i+1}/{SYNTHETIC_RECORDS}] embedding: {embed_text[:60]}")
        embedding = generate_embedding(embed_text)

        records.append({
            "record_id": f"real-{i:04d}",
            "violation_type": vtype,
            "field_name": field,
            "original_value": orig,
            "corrected_value": corrected,
            "category": random.choice(categories),
            "brand": random.choice(brands),
            "approved": approved,
            "approval_source": "HUMAN" if approved else "REJECTED",
            "approver_email": "approver@example.com" if approved else None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "embedding": embedding,
        })

    return records


def main():
    parser = argparse.ArgumentParser(description="Argus BigQuery setup")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Wipe existing records and re-seed with real text-embedding-004 vectors.",
    )
    args = parser.parse_args()

    client = bigquery.Client(project=PROJECT)

    # Create dataset
    dataset_ref = bigquery.Dataset(f"{PROJECT}.{DATASET}")
    dataset_ref.location = "US"
    try:
        client.create_dataset(dataset_ref)
        print(f"Created dataset {DATASET}")
    except Conflict:
        print(f"Dataset {DATASET} already exists — skipping")

    # Create table
    table_ref = client.dataset(DATASET).table(TABLE)
    table = bigquery.Table(table_ref, schema=SCHEMA)
    try:
        client.create_table(table)
        print(f"Created table {TABLE}")
    except Conflict:
        print(f"Table {TABLE} already exists — skipping")

    if args.overwrite:
        print(f"\nOverwrite mode: deleting all rows from {TABLE}...")
        client.query(
            f"DELETE FROM `{PROJECT}.{DATASET}.{TABLE}` WHERE TRUE"
        ).result()
        print("Deleted. Generating real embeddings (50 records × Vertex AI)...")
        records = _real_embedding_records()
    else:
        existing = client.query(
            f"SELECT COUNT(*) as cnt FROM `{PROJECT}.{DATASET}.{TABLE}`"
        ).result()
        count = next(existing)["cnt"]
        if count >= SYNTHETIC_RECORDS:
            print(f"Table already has {count} records — skipping load (use --overwrite to reseed)")
            records = None
        else:
            records = _synthetic_records()

    if records is not None:
        errors = client.insert_rows_json(f"{PROJECT}.{DATASET}.{TABLE}", records)
        if errors:
            print(f"Insert errors: {errors}")
            raise RuntimeError("Failed to insert records")
        print(f"Inserted {len(records)} records")

    # Smoke test: VECTOR_SEARCH
    print("\nRunning VECTOR_SEARCH smoke test...")
    test_vec = _random_unit_vector(EMBEDDING_DIM)
    vec_str = "[" + ",".join(str(x) for x in test_vec) + "]"

    query = f"""
        SELECT
            base.record_id,
            base.violation_type,
            base.field_name,
            base.corrected_value,
            base.approved,
            distance
        FROM
            VECTOR_SEARCH(
                TABLE `{PROJECT}.{DATASET}.{TABLE}`,
                'embedding',
                (SELECT {vec_str} AS embedding),
                top_k => 3,
                distance_type => 'COSINE'
            )
        ORDER BY distance ASC
    """
    results = list(client.query(query).result())
    if not results:
        raise RuntimeError("VECTOR_SEARCH returned no results")

    print(f"VECTOR_SEARCH OK — top {len(results)} results:")
    for row in results:
        print(f"  {row['record_id']} | {row['violation_type']}:{row['field_name']} | dist={row['distance']:.4f}")

    print("\nSetup complete.")


if __name__ == "__main__":
    main()
