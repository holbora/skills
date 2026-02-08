---
name: openapi-resource
description: Implement a resource from the OpenAPI spec test-first. Writes a failing test, stubs the controller, verifies failure, then implements and verifies success.
argument-hint: "[resource or endpoint to implement, e.g. users or GET /users]"
---

Implement the endpoint using a test-first workflow. Follow these steps in order:

## 1. Read the spec

Open `openapi.yaml` and locate the endpoint matching `$ARGUMENTS`. Extract: path, method, operationId, `x-eov-operation-handler`, request/response schemas, and all response status codes.

If the endpoint is not in the spec, stop and tell the user to run `/openapi-design` first.

## 2. Read existing files

- Check if `test/{handler}.test.js` exists (where `{handler}` is the `x-eov-operation-handler` value)
- Check if `src/controllers/{handler}.js` exists

## 3. Write the test

Create or update `test/{handler}.test.js` following this pattern:

```js
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { app } from '../server.js';

describe('{handler}', () => {
  let server;
  let baseUrl;

  before(() => {
    server = app.listen(0);
    const { port } = server.address();
    baseUrl = `http://localhost:${port}`;
  });

  after(() => server.close());

  // one `it` block per response scenario in the spec
});
```

Write one `it` block for each response status code defined in the spec (200, 201, 400, 404, 409, etc.). Test the happy path and every error scenario.

## 4. Stub the controller

If the controller file does not exist yet, create a minimal stub at `src/controllers/{handler}.js` that exports the operationId function and returns a 501 response:

```js
export function operationId(request, response) {
  response.status(501).json({ message: 'not implemented' });
}
```

This lets the server boot so the test can run and fail.

## 5. Run tests — expect failure

Rebuild Docker and run tests:

```
docker build --target dev -t api-dev .
docker run --rm --name $(basename $PWD) api-dev npm test
```

Confirm the new test fails (501 instead of expected status, wrong response body, etc.). If it passes already, the test is not asserting enough — go back and strengthen it.

## 6. Write the controller

Implement the real logic in `src/controllers/{handler}.js` to make all tests pass.

## 7. Run tests — expect success

Rebuild Docker and run tests again:

```
docker build --target dev -t api-dev .
docker run --rm --name $(basename $PWD) api-dev npm test
```

All tests must pass. If any fail, fix the controller and re-run until green.

Ask: $ARGUMENTS
