# Alliance Amazon Enrichment (CLI)

Local, file-based tooling to generate Amazon FBM listing drafts from a **facts card** and to run **compliance scans** for regulated/forbidden claims.

- Read-only by default: commands print to stdout unless `--out` is provided.
- No network required: Shopify import is supported from JSON dumps.

## Requirements

- Python 3.10+ (`python3`)

## Quickstart

Generate a facts card template:

```bash
python3 -m alliance_amazon facts init --out examples/facts_card_template.json
```

Validate a facts card:

```bash
python3 -m alliance_amazon facts validate examples/facts_isopropyl_alcohol.json
```

Generate a listing draft JSON:

```bash
python3 -m alliance_amazon listing generate \
  --facts examples/facts_isopropyl_alcohol.json \
  --size "1 Gallon" \
  --out examples/listing_isopropyl_alcohol.json
```

Generate a listing draft and rewrite copy with Gemini (`gemini-3-flash-preview`):

```bash
export GEMINI_API_KEY="..."
python3 -m alliance_amazon listing generate \
  --facts examples/facts_isopropyl_alcohol.json \
  --size "1 Gallon" \
  --llm-provider gemini \
  --llm-model gemini-3-flash-preview \
  --out examples/listing_isopropyl_alcohol_gemini.json
```

Render the listing draft to a readable format:

```bash
python3 -m alliance_amazon listing render \
  --listing examples/listing_isopropyl_alcohol.json
```

Scan a listing JSON for compliance risks:

```bash
python3 -m alliance_amazon compliance scan examples/listing_isopropyl_alcohol.json
```

## Keywords

Suggest keywords from a facts card (and pre-filter hard-blocked terms):

```bash
python3 -m alliance_amazon keywords suggest --facts examples/facts_isopropyl_alcohol.json
```

## Amazon Flat-File Export (XLSM Template)

The provided Amazon category template `.xlsm` files contain a header row of attribute keys. This CLI can generate a TSV/CSV with those headers plus one populated row.

Describe the template headers:

```bash
python3 -m alliance_amazon flatfile describe --xlsm "LAB_CHEMICAL (Blank).xlsm" --sheet Template | head
```

Generate a TSV row for upload (aligned to the template headers):

```bash
python3 -m alliance_amazon flatfile generate \
  --xlsm "LAB_CHEMICAL (Blank).xlsm" \
  --facts examples/facts_isopropyl_alcohol.json \
  --size "1 Gallon" \
  --product-type LAB_CHEMICAL \
  --out out/lab_chemical.tsv
```

## Shopify Import (No Network)

If you have Shopify Admin API dumps saved to disk:

```bash
python3 -m alliance_amazon facts from-shopify \
  --product examples/shopify_product_example.json \
  --metafields examples/shopify_metafields_example.json \
  --sku "AC-12345" \
  --out examples/facts_from_shopify.json
```

## Shopify Import (Live by SKU)

Set environment variables (see `.env.example`). Required:

- `SHOPIFY_SHOP_DOMAIN=alliance-chemical-store.myshopify.com`
- `SHOPIFY_ACCESS_TOKEN=...`

Fetch the product + metafields for a SKU:

```bash
python3 -m alliance_amazon shopify fetch --sku "AC-IPA-99-1G" --out out/shopify_AC-IPA-99-1G.json
```

Generate a listing draft directly from Shopify data (auto-filters/redacts blocked terms from Shopify sources):

```bash
python3 -m alliance_amazon listing from-shopify --sku "AC-IPA-99-1G" --out out/listing_AC-IPA-99-1G.json
```

Optional rewrite pass with Gemini:

```bash
export GEMINI_API_KEY="..."
python3 -m alliance_amazon listing from-shopify \
  --sku "AC-IPA-99-1G" \
  --llm-provider gemini \
  --llm-model gemini-3-flash-preview \
  --out out/listing_AC-IPA-99-1G_gemini.json
```

## Amazon SP-API Update (Dry-Run Default)

Build a Listings Items PATCH request body from a listing JSON:

```bash
python3 -m alliance_amazon amazon build-patch --listing out/listing_AC-IPA-99-1G.json --out out/spapi_patch.json
```

Publish to Amazon (requires SP-API + LWA + AWS env vars; see `.env.example`):

```bash
python3 -m alliance_amazon amazon update \
  --sku "AC-IPA-99-1G" \
  --listing out/listing_AC-IPA-99-1G.json \
  --publish --i-understand
```

## Output Format

`listing generate` produces a JSON object with:

- `title`
- `bullets` (array)
- `description`
- `backend_search_terms` (auto-truncated to 250 UTF-8 bytes)
- `a_plus_markdown` and `a_plus` (draft content structures)
- `compliance_findings` + `compliance_status`

## Notes

- This tool does **not** publish to Amazon/Seller Central.
- Grade terminology is treated as **hard-blocked** unless the grade term appears in `product_name` (Shopify title), per the master plan.
- Gemini requests require network access and `GEMINI_API_KEY`; in restricted environments, run with approvals enabled.

## Tests

```bash
python3 -m unittest discover -s tests
```
