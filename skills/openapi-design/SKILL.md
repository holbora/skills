---
name: openapi-design
description: Design or extend the OpenAPI spec. Use when adding endpoints, resources, or modifying the API contract.
argument-hint: "[description of the endpoint or resource to add]"
---

Read `openapi.yaml` before making any changes.

## RESTful Design

- Plural nouns for resources (`/users`, not `/user`)
- Nested paths for relationships (`/users/{userId}/posts`)
- Correct HTTP methods: GET (read), POST (create), PUT (full replace), PATCH (partial update), DELETE (remove)
- Correct status codes: 200, 201, 204, 400, 404, 409, 422, 500
- Query parameters for filtering, sorting, and pagination on list endpoints

## Spec Completeness

Every endpoint must have:
- A `description`
- An `operationId` matching the exported function name in the controller
- An `x-eov-operation-handler` pointing to the controller file under `src/controllers/`
- All possible response codes with descriptions

Every property in every schema must have a `type` and `description`.

Every parameter must have a `description`, `required` flag, and `schema` with `type`.

Every request body must have a `description` and `content` block with `application/json` schema.

## Schema Organization

- Define reusable schemas, parameters, and responses under `components/`
- Always use `$ref` — never inline schemas, even if they appear only once
- Name schemas as singular PascalCase nouns (`User`, `Post`, `ErrorResponse`)

## Workflow

1. Present the planned endpoint design (method, path, request/response shapes) before writing
2. Add or update paths in `openapi.yaml`
3. Tell the user to run `/openapi-resource` to implement the resource test-first

Ask: $ARGUMENTS
