## ADDED Requirements

### Requirement: Documented socket entrypoints are importable from the package root

The distribution SHALL expose `ClientSocket` and `ServerSocket` from the top-level `socket_package` namespace alongside existing documented exports, without removing the existing `socket_package.Client` and `socket_package.Server` import paths.

#### Scenario: Import client from package root

- **WHEN** a consumer runs `from socket_package import ClientSocket`
- **THEN** the import succeeds and `ClientSocket` is the same class as `socket_package.Client.ClientSocket`

#### Scenario: Import server from package root

- **WHEN** a consumer runs `from socket_package import ServerSocket`
- **THEN** the import succeeds and `ServerSocket` is the same class as `socket_package.Server.ServerSocket`

### Requirement: Manual demos are isolated from pytest-discovered tests

Automated tests under `tests/` SHALL remain discoverable as `test_*.py` at the `tests/` root (or existing pytest configuration). Manual integration entrypoints and shared sample protocol code used only by those demos SHALL reside under `tests/examples/` so the `tests/` root primarily lists automated tests.

#### Scenario: Demo scripts live under examples

- **WHEN** a maintainer lists the `tests/` directory
- **THEN** `mainServer.py` and `mainClient.py` are not present at `tests/` root and are present under `tests/examples/`

#### Scenario: Documented demo commands stay valid with updated paths

- **WHEN** a user follows project documentation to start demos
- **THEN** the documented commands use `tests/examples/mainServer.py` and `tests/examples/mainClient.py` (or equivalent documented paths) and those scripts run successfully from the repository root with `uv run python …`

### Requirement: Protocol subpackage is explicit

The installed package SHALL include `socket_package/Protocol/__init__.py` so `socket_package.Protocol` is a regular subpackage boundary.

#### Scenario: Protocol package initialization exists

- **WHEN** the sdist/wheel is built and installed
- **THEN** `socket_package.Protocol` resolves as a package with an explicit `__init__` module file present in the source tree

### Requirement: Runtime dependencies match actual usage

The project SHALL NOT declare `requests` as a direct runtime dependency in `pyproject.toml` unless source or documented runtime behavior requires it.

#### Scenario: Lockfile matches pyproject after dependency removal

- **WHEN** `pyproject.toml` no longer lists `requests` under `[project] dependencies`
- **THEN** `uv lock` (or equivalent) is refreshed so the lockfile does not require `requests` solely for this package root project metadata
