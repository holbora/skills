#!/usr/bin/env python3
"""
OpenAPI 3.0/3.1 Validator with Schema Validation and Linting

Usage:
    python validate_openapi.py <path-to-spec>

Outputs validation results including schema errors and linting warnings.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from openapi_spec_validator import validate
    from openapi_spec_validator.readers import read_from_filename
    from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False


def load_spec(file_path: str) -> dict:
    """Load an OpenAPI spec from a file (YAML or JSON)."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text()

    if path.suffix in ('.yaml', '.yml'):
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML files. Install with: pip install pyyaml")
        return yaml.safe_load(content)
    elif path.suffix == '.json':
        return json.loads(content)
    else:
        # Try YAML first, then JSON
        if YAML_AVAILABLE:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                pass
        return json.loads(content)


def validate_schema(file_path: str) -> list[str]:
    """Validate the OpenAPI spec against the official schema."""
    errors = []

    if not VALIDATOR_AVAILABLE:
        errors.append("ERROR: openapi-spec-validator not installed. Install with: pip install openapi-spec-validator")
        return errors

    try:
        validate(read_from_filename(file_path))
    except OpenAPIValidationError as e:
        errors.append(f"SCHEMA ERROR: {e.message if hasattr(e, 'message') else str(e)}")
    except Exception as e:
        error_msg = str(e).strip()
        if error_msg:
            errors.append(f"ERROR: {error_msg}")

    return errors


def lint_spec(spec: dict) -> list[str]:
    """Run linting checks on the OpenAPI spec."""
    warnings = []

    # Check OpenAPI version
    openapi_version = spec.get('openapi', '')
    if not openapi_version:
        warnings.append("LINT: Missing 'openapi' version field")
    elif not openapi_version.startswith('3.'):
        warnings.append(f"LINT: OpenAPI version '{openapi_version}' is not 3.x")

    # Check info section
    info = spec.get('info', {})
    if not info:
        warnings.append("LINT: Missing 'info' section")
    else:
        if not info.get('title'):
            warnings.append("LINT: Missing 'info.title'")
        if not info.get('version'):
            warnings.append("LINT: Missing 'info.version'")
        if not info.get('description'):
            warnings.append("LINT: Missing 'info.description' (recommended)")

    # Check paths
    paths = spec.get('paths', {})
    if not paths:
        warnings.append("LINT: No paths defined")
    else:
        for path, path_item in paths.items():
            # Check path naming
            if not path.startswith('/'):
                warnings.append(f"LINT: Path '{path}' should start with '/'")

            if path_item is None:
                continue

            # Check operations
            for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                operation = path_item.get(method)
                if operation:
                    op_id = f"{method.upper()} {path}"

                    # Check operationId
                    if not operation.get('operationId'):
                        warnings.append(f"LINT: {op_id} missing 'operationId'")

                    # Check summary/description
                    if not operation.get('summary') and not operation.get('description'):
                        warnings.append(f"LINT: {op_id} missing 'summary' or 'description'")

                    # Check responses
                    responses = operation.get('responses', {})
                    if not responses:
                        warnings.append(f"LINT: {op_id} has no responses defined")
                    else:
                        # Check for success response
                        has_success = any(str(code).startswith('2') for code in responses.keys())
                        if not has_success and 'default' not in responses:
                            warnings.append(f"LINT: {op_id} has no success (2xx) response")

                        # Check response descriptions
                        for code, response in responses.items():
                            if response and not response.get('description'):
                                warnings.append(f"LINT: {op_id} response '{code}' missing description")

    # Check components/schemas
    components = spec.get('components', {})
    schemas = components.get('schemas', {})
    for schema_name, schema in schemas.items():
        if schema and not schema.get('description'):
            warnings.append(f"LINT: Schema '{schema_name}' missing description (recommended)")

        # Check for type definition
        if schema and not schema.get('type') and not schema.get('$ref') and not schema.get('allOf') and not schema.get('oneOf') and not schema.get('anyOf'):
            warnings.append(f"LINT: Schema '{schema_name}' has no type definition")

    # Check security definitions if security is used
    security = spec.get('security', [])
    security_schemes = components.get('securitySchemes', {})
    if security and not security_schemes:
        warnings.append("LINT: Security requirements defined but no securitySchemes in components")

    # Check for servers
    servers = spec.get('servers', [])
    if not servers:
        warnings.append("LINT: No servers defined (recommended for clarity)")

    return warnings


def main():
    parser = argparse.ArgumentParser(description='Validate OpenAPI 3.x specifications')
    parser.add_argument('spec_file', help='Path to the OpenAPI spec file (YAML or JSON)')
    parser.add_argument('--lint-only', action='store_true', help='Skip schema validation, only run linting')
    parser.add_argument('--schema-only', action='store_true', help='Skip linting, only run schema validation')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    results = {
        'file': args.spec_file,
        'valid': True,
        'schema_errors': [],
        'lint_warnings': []
    }

    try:
        # Load the spec
        spec = load_spec(args.spec_file)

        # Schema validation
        if not args.lint_only:
            results['schema_errors'] = validate_schema(args.spec_file)
            if results['schema_errors']:
                results['valid'] = False

        # Linting
        if not args.schema_only:
            results['lint_warnings'] = lint_spec(spec)

    except FileNotFoundError as e:
        results['valid'] = False
        results['schema_errors'] = [str(e)]
    except Exception as e:
        results['valid'] = False
        results['schema_errors'] = [f"Failed to parse spec: {e}"]

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"OpenAPI Validation: {args.spec_file}")
        print(f"{'='*60}\n")

        if results['schema_errors']:
            print("❌ SCHEMA ERRORS:")
            for error in results['schema_errors']:
                print(f"   • {error}")
            print()

        if results['lint_warnings']:
            print("⚠️  LINT WARNINGS:")
            for warning in results['lint_warnings']:
                print(f"   • {warning}")
            print()

        if results['valid'] and not results['lint_warnings']:
            print("✅ Specification is valid with no warnings!\n")
        elif results['valid']:
            print(f"✅ Specification is valid (with {len(results['lint_warnings'])} warnings)\n")
        else:
            print(f"❌ Specification is INVALID\n")

    # Exit code
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()
