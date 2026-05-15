## Why

The library’s packaging and documentation drifted from actual import paths and carried an unused runtime dependency. Aligning the public import surface, test layout, and dependencies reduces confusion for integrators and keeps the install footprint honest.

## What Changes

- Re-export `ClientSocket` and `ServerSocket` from the top-level `socket_package` package (alongside existing exports) so README “core API” matches `from socket_package import …`.
- Add an explicit `socket_package.Protocol` subpackage initializer (`Protocol/__init__.py`) for a clear, conventional package boundary.
- Move manual demo entrypoints and shared sample protocol/helpers out of the flat `tests/` root into `tests/examples/` (or equivalent) so automated `test_*.py` files stay primary under `tests/`; update imports and AGENTS/README references as needed.
- Remove the unused `requests` runtime dependency from `pyproject.toml` and refresh `uv.lock`.
- No wire-protocol or framing behavior changes.

## Capabilities

### New Capabilities

- `package-distribution`: Requirements for public import surface (top-level re-exports), dependency hygiene, and documentation alignment for installing and importing `socket_package`.

### Modified Capabilities

- (none — no existing `openspec/specs/` baseline)

## Impact

- Affected: `src/socket_package/__init__.py`, new `src/socket_package/Protocol/__init__.py`, `pyproject.toml`, `uv.lock`, `tests/` layout (moved example modules), `README.md`, `AGENTS.md` (paths for running examples), any tests or samples that imported moved modules.
