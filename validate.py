#!/usr/bin/env python3
"""Validate every products/*.json record against schema/product.schema.json.

Runs two suites:
  1. positive - every product file must validate cleanly
  2. strictness negatives - each mutation of a known-good record must be REJECTED

Requires: pip install jsonschema rfc3986-validator
The rfc3986-validator package is what makes format:"uri" actually assert
instead of being silently skipped by jsonschema.

Exit code 0 = everything as expected, 1 = at least one unexpected result.
"""

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

REPO = Path(__file__).resolve().parent
SCHEMA_PATH = REPO / "schema" / "product.schema.json"
PRODUCTS_DIR = REPO / "products"

# Each case mutates a deep copy of a known-good record and must be rejected.
NEGATIVE_CASES = [
    ("root unexpected property (color_profile)",
     lambda d: d.update({"color_profile": "GRACoL"})),
    ("public unexpected property (price)",
     lambda d: d["public"].update({"price": 129.0})),
    ("internal unexpected property (cost)",
     lambda d: d["internal"].update({"cost": 42})),
    ("missing required public field (sides)",
     lambda d: d["public"].pop("sides")),
    ("invalid sides enum value",
     lambda d: d["public"].update({"sides": "DS"})),
    ("negative dimension",
     lambda d: d["public"].update({"finished_w_in": -1})),
    ("non-integer dpi_floor",
     lambda d: d["public"].update({"dpi_floor": 50.5})),
    ("malformed uri (pricing_guide_url)",
     lambda d: d["public"].update({"pricing_guide_url": "not a url"})),
    ("empty-string template_drive_id",
     lambda d: d["internal"].update({"template_drive_id": ""})),
    ("string ordant_product_id (must be numeric)",
     lambda d: d["internal"].update({"ordant_product_id": "12345"})),
    ("zero ordant_product_id",
     lambda d: d["internal"].update({"ordant_product_id": 0})),
    ("template_repo_path outside templates/ folder",
     lambda d: d["internal"].update({"template_repo_path": "other/AF-AF-11-DS.ai"})),
    ("template_repo_path with wrong extension",
     lambda d: d["internal"].update({"template_repo_path": "templates/AF-AF-11-DS.pdf"})),
]


def build_validator():
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    format_checker = FormatChecker()
    if "uri" not in format_checker.checkers:
        sys.exit("uri format checker inactive - pip install rfc3986-validator")
    return Draft202012Validator(schema, format_checker=format_checker)


def main():
    validator = build_validator()
    print(f"schema self-check: PASS ({SCHEMA_PATH.relative_to(REPO)} is valid 2020-12)\n")

    ok = True
    product_files = sorted(PRODUCTS_DIR.glob("*.json"))
    if not product_files:
        sys.exit(f"no product files found in {PRODUCTS_DIR}")

    print("-- positive tests --")
    for path in product_files:
        errors = sorted(validator.iter_errors(json.loads(path.read_text())),
                        key=lambda e: list(e.path))
        if errors:
            ok = False
            print(f"FAIL {path.relative_to(REPO)}")
            for err in errors:
                print(f"        {list(err.path)}: {err.message}")
        else:
            print(f"PASS {path.relative_to(REPO)}")

    print("\n-- strictness negative tests (rejection is the pass condition) --")
    baseline = json.loads(product_files[0].read_text())
    for name, mutate in NEGATIVE_CASES:
        candidate = copy.deepcopy(baseline)
        mutate(candidate)
        errors = list(validator.iter_errors(candidate))
        if errors:
            print(f"PASS correctly rejected - {name}: {errors[0].message}")
        else:
            ok = False
            print(f"FAIL wrongly accepted - {name}")

    print("\nOVERALL: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
