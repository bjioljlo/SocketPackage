## Context

The package uses a `src/` layout with `socket_package` as the installable root. Documentation lists `ClientSocket` and `ServerSocket` as first-class API, but they were only importable via subpackages. Sample/demo modules lived alongside `test_*.py` under `tests/`, blurring automated tests and manual demos. `requests` was declared as a runtime dependency but is unused in `src/`. `Protocol/` had no `__init__.py`, relying on implicit namespace-style layout.

## Goals / Non-Goals

**Goals:**

- Align top-level `socket_package` exports with documented “core API” for sockets.
- Separate manual integration demos from pytest-discovered tests via `tests/examples/`.
- Make `socket_package.Protocol` an explicit subpackage.
- Drop unused `requests` and refresh the lockfile.

**Non-Goals:**

- Renaming modules to PEP 8 snake_case (breaking, out of scope).
- Changing frame format, protocol kinds, or socket runtime behavior.
- Adding CI or new tooling beyond what is needed to verify the change.

## Decisions

1. **Top-level re-exports** — Import `ClientSocket` and `ServerSocket` in `socket_package/__init__.py` from `.Client` and `.Server` and append to `__all__`. Rationale: minimal user-facing churn; matches README. Alternative (document-only) rejected because the user asked for a direct fix.

2. **`tests/examples/` layout** — Move all sample managers, recv protocols, shared `ProtocolKinds.py`, and `mainServer.py` / `mainClient.py` into `tests/examples/`. Add `tests/__init__.py` and `tests/examples/__init__.py` so tests can use stable imports `from tests.examples...`. Rationale: keeps sibling imports inside `examples/` working when running `uv run python tests/examples/mainServer.py` (script directory on `sys.path`). Update `test_config_and_sample_protocols.py` to import from `tests.examples`.

3. **`Protocol/__init__.py`** — Add a minimal package docstring (and optional empty `__all__`) without re-exporting everything, to avoid circular imports and duplicate public surfaces. Rationale: satisfies “explicit subpackage” without redesigning imports.

4. **Dependencies** — Remove `requests` from `[project] dependencies` and run `uv lock` so `uv.lock` no longer pins it for this package.

## Risks / Trade-offs

- **[Risk] Anyone importing moved modules by top-level name** (e.g. undocumented `from ProtocolKinds import`) **breaks** → **Mitigation**: only `tests/test_config_and_sample_protocols.py` referenced those; demos use same-directory imports inside `examples/`.

- **[Risk] `tests` as a package** could interact oddly with some tools → **Mitigation**: empty `__init__.py` only; run full `pytest` to confirm.

## Migration Plan

Ship in one version: users switch `from socket_package.Client import ClientSocket` to `from socket_package import ClientSocket` optionally; old import paths remain valid. Demo commands change to `tests/examples/mainServer.py` and `tests/examples/mainClient.py`.

## Open Questions

- None for this change set.
