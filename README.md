# Heritage Product Info

Authoritative JSON product registry for HBS / Find Swag. It is the single source of truth
for the product facts used in proofing and preflight (finished size, sides, corner radius,
safe zone, dpi floor) and for the customer-safe product copy shown outside the shop.

One file per SKU, validated against a strict JSON Schema, so that automated proofing tools
and customer-facing surfaces read the same numbers instead of each carrying their own copy.

## Repository structure

| Path | Purpose |
| --- | --- |
| `schema/product.schema.json` | JSON Schema (Draft 2020-12) that every product record must satisfy. Strict: unknown fields are rejected. |
| `products/` | One JSON file per SKU, named after the SKU. |
| `validate.py` | Validates every file in `products/` against the schema and runs the strictness negative tests. |
| `VALIDATION.md` | Current validation report: tooling, per-file results, negative-test results, and open items. |

## Record shape: exactly two blocks

Every product file contains exactly two blocks, plus an optional `$schema` pointer for
editor support.

**`public`** - safe to expose to customers and to reuse in storefront or proof-facing
tooling. Holds identity and copy (`sku`, `ordant_product_name`, `product_family`,
`description_short`, `description_long`), print geometry and preflight limits
(`finished_w_in`, `finished_h_in`, `sides`, `corner_radius_in`, `safe_zone_in`,
`dpi_floor`, `wide_format`, `default_substrate`), and public links (`hero_image_url`,
`template_download_url`, `pricing_guide_url`).

**`internal`** - operational data, not for customer display. Holds
`ordant_product_id` (numeric Ordant primary ID), `vendor`, `vendor_sku`,
`template_drive_id`, `template_local_cache`, and `notes`. The `notes` field is where
provenance, unresolved measurements, and verification warnings are recorded.

The split is enforced by the schema. Adding a field to either block requires a schema
change, which keeps internal data from leaking into public payloads by accident.

## Templates and binaries

No template artwork or binaries are stored in this repository. Production templates stay
in Google Drive and are referenced by ID in `internal.template_drive_id`, with
`internal.template_local_cache` giving the expected local cache path for tooling that
pulls them down.

Public `hero_image_url` and `template_download_url` values are pending generation and are
currently `null` for every SKU. They will be populated once customer-facing assets exist.

## Pricing

Pricing is never stored, computed, or derived in this repository. There are no price or
cost fields, and the schema's strict mode prevents one from being added without an
explicit schema change.

The customer PO is the source of truth for price. Where a `pricing_guide_url` is present
it is a human reference link only - a deep link for a person to open - and must not be
scraped or treated as a pricing feed.

## Seed SKUs

Slice 1 seeds three SKUs:

| SKU | Ordant product name | Family |
| --- | --- | --- |
| `TBD-6-S` | 6FT Table Top Banner - S | Tabletop Banner Display |
| `CAN-10x10` | 10x10 Pop-Up Canopy Tent Top | Pop-Up Canopy Tent Top |
| `CW-10-DS` | Canopy Wall - 40mm Hex Frame - 10ft / Double Sided / Full Wall | Pop-Up Canopy Full Wall |

## How the registry grows

The registry grows incrementally, driven by real work: a SKU is added or filled in when an
actual job touches it and its facts are confirmed. No bulk back-fill is required, and
completeness against the full catalog is not a goal or a blocker. A SKU being absent means
no job has needed it yet, not that anything is missing.

Existing product descriptions and other non-pricing specification facts may be imported
from the pricing guide (PG) later, as a convenience source for copy and specs. That import
is optional and does not change the pricing rule above: pricing values and pricing
computation stay out of this repository permanently, regardless of where specification text
is sourced from.

## Validation

```bash
pip install jsonschema rfc3986-validator
python3 validate.py
```

`rfc3986-validator` is required, not optional: without it `jsonschema` silently skips
`format: "uri"` checks. `validate.py` exits `0` only when every product file validates and
every strictness negative test is correctly rejected. Current results are in
`VALIDATION.md`.

## The meaning of `null`

`null` means **verified unresolved** - the value was looked for and is not yet confirmed.
It does not mean blank, not applicable, or forgotten.

Every field is required on every record, so a fact is never simply missing; it is either a
confirmed value or an explicit `null`. Guessed or nominal values are not published in
`public`. When a nominal figure exists but has not been confirmed against the factory
template, the public field stays `null` and the figure is recorded in `internal.notes`
along with what must happen to resolve it. Consumers should treat `null` as "do not rely
on this yet," never as zero.
