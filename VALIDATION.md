# Validation Report - Slice 1 (Product Registry MVP)

Date: 2026-07-29
Schema: `schema/product.schema.json` (JSON Schema Draft 2020-12)
Validator script: `validate.py` (in this repo)

## Tooling

| Item | Value |
| --- | --- |
| Validator | Python `jsonschema` 4.26.0 (`Draft202012Validator`) |
| Format assertion | `jsonschema.FormatChecker()` with `rfc3986-validator` 0.1.1 installed, so `format: "uri"` is actually enforced rather than silently skipped |
| Python | python3 |
| Schema self-check | `Draft202012Validator.check_schema()` - PASS (schema itself is a valid 2020-12 schema) |

Reproduce:

```bash
pip3 install jsonschema rfc3986-validator
cd /home/user/workspace/heritage-product-info
python3 validate.py
```

`validate.py` runs both suites below and exits 0 only if every positive file validates
and every negative case is rejected. It resolves paths relative to its own location, so
it can be run from any working directory.

The schema intentionally has **no `$id`**. The final published raw URL is not known yet,
and a placeholder domain would be a fake resolvable identifier, so `$id` will be added
only once the real hosting location is settled. Each product file's `$schema` value is a
relative path (`../schema/product.schema.json`) that works locally today.

## Positive results

| File | Result |
| --- | --- |
| `products/CAN-10x10.json` | PASS |
| `products/CW-10-DS.json` | PASS |
| `products/TBD-6-S.json` | PASS |

All three records validate with zero errors, including the `$schema` pointer to
`../schema/product.schema.json`, all 16 required `public` fields, and all 6 required
`internal` fields.

The one non-null URL in the set - the `CW-10-DS` pricing guide deep link with the
`#gid=...&range=43:43` fragment - passes `format: "uri"` under the RFC 3986 checker.

## Strictness / negative tests

Each case mutates a known-good record and is expected to be **rejected**. "PASS" means
the schema correctly refused the document.

| # | Negative case | Result | Rejection reason reported |
| --- | --- | --- | --- |
| 1 | Unexpected property at root (`color_profile`) | PASS | `Additional properties are not allowed ('color_profile' was unexpected)` |
| 2 | Unexpected property in `public` (`price`) | PASS | `Additional properties are not allowed ('price' was unexpected)` |
| 3 | Unexpected property in `internal` (`cost`) | PASS | `Additional properties are not allowed ('cost' was unexpected)` |
| 4 | Missing required field `public.sides` | PASS | `'sides' is a required property` |
| 5 | Invalid `sides` enum value (`"DS"`) | PASS | `'DS' is not one of ['SS', 'DS-same-art', 'DS-two-files']` |
| 6 | Negative `finished_w_in` (`-1`) | PASS | `-1 is less than the minimum of 0` |
| 7 | Non-integer `dpi_floor` (`50.5`) | PASS | `50.5 is not of type 'integer'` |
| 8 | Malformed `pricing_guide_url` (`"not a url"`) | PASS | `'not a url' is not a 'uri'` |
| 9 | Empty-string `template_drive_id` | PASS | `'' should be non-empty` |
| 10 | String `ordant_product_id` (`"12345"`) | PASS | `'12345' is not of type 'integer', 'null'` |
| 11 | Zero `ordant_product_id` (`0`) | PASS | `0 is less than the minimum of 1` |

Cases 10 and 11 were added when `internal.ordant_product_id` moved from a nullable
non-empty string to `$defs.nullablePositiveInteger` (`type: ["integer", "null"]`,
`minimum: 1`), matching the numeric primary IDs the Ordant API issues. A real ID such as
`104882` validates; a stringified ID or a non-positive one does not.

Cases 2 and 3 are the ones that matter most for the pricing prohibition: a price-bearing
field cannot be smuggled into either block, because `additionalProperties: false` is set
at the root and on both `public` and `internal`.

## Overall

**PASS** - 3/3 product files valid, 11/11 strictness negative tests correctly rejected,
`validate.py` exit code 0.

## Open items (not schema failures)

Each of these is recorded in the relevant record's `internal.notes`:

- `TBD-6-S`: `safe_zone_in` of 1.0 in comes from the House Template v2 reference build default and still needs verification against the factory die. Because it is provisional, `description_long` does not publish it as an authoritative requirement - the public text says only to keep critical content clear of the finished edge and that the exact safe zone is confirmed against the production template. `template_drive_id` unresolved.
- `CAN-10x10`: 117.6 in runs edge-to-edge across the bottom valance per HBS-12569 (which also calls out a 17 in valance); factory geometry stays authoritative. `safe_zone_in` pending factory-template measurement.
- `CW-10-DS`: exact finished dimensions unresolved (nominal 10 x 7 ft recorded in notes only); factory-template measurement must populate them before automated preflight is enabled.
- All three: `ordant_product_id` null (unassigned) and `default_substrate` null (unconfirmed).
