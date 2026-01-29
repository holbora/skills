---
name: openapi-validator
description: Validate OpenAPI 3.0/3.1 specifications for schema correctness and best practices. Use when asked to validate, check, or lint an OpenAPI spec file (YAML or JSON). Triggers on phrases like "check if api.yaml is valid", "validate this openapi spec", "lint my openapi file", or "is this API spec correct".
---

# OpenAPI Validator

Validate OpenAPI 3.0/3.1 specifications for schema correctness and lint for best practices.

## Quick Start

To validate an OpenAPI spec:

```bash
python scripts/validate_openapi.py <path-to-spec>
```

## Validation Modes

| Flag | Description |
|------|-------------|
| (none) | Full validation: schema + linting |
| `--schema-only` | Only check schema validity |
| `--lint-only` | Only run best practice checks |
| `--json` | Output results as JSON |

## Requirements

Install dependencies before first use:

```bash
pip install openapi-spec-validator pyyaml
```

## What Gets Checked

### Schema Validation
- Valid OpenAPI 3.x structure
- Required fields present
- Correct types and formats
- Valid $ref references

### Linting Checks
- `info.title`, `info.version`, `info.description` present
- All operations have `operationId`
- All operations have `summary` or `description`
- All responses have descriptions
- Success (2xx) responses defined
- Schemas have type definitions and descriptions
- Security schemes defined when security is used
- Servers array populated
- Paths start with `/`

## Example Output

```
============================================================
OpenAPI Validation: api.yaml
============================================================

⚠️  LINT WARNINGS:
   • LINT: GET /users missing 'operationId'
   • LINT: Schema 'User' missing description (recommended)

✅ Specification is valid (with 2 warnings)
```
