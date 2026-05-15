## 1. OpenSpec & packaging metadata

- [x] 1.1 Remove unused `requests` from `pyproject.toml` and refresh `uv.lock` with `uv lock`

## 2. Public API and Protocol package boundary

- [x] 2.1 Re-export `ClientSocket` and `ServerSocket` from `src/socket_package/__init__.py` and extend `__all__`
- [x] 2.2 Add `src/socket_package/Protocol/__init__.py` as an explicit subpackage (minimal content)

## 3. Tests vs examples layout

- [x] 3.1 Add `tests/__init__.py` and `tests/examples/__init__.py`
- [x] 3.2 Move demo and sample modules into `tests/examples/` (`mainServer.py`, `mainClient.py`, `ProtocolKinds.py`, `Sample*.py`, `*RecvMsgProtocol.py`)
- [x] 3.3 Update `tests/test_config_and_sample_protocols.py` imports to `tests.examples` where needed

## 4. Documentation

- [x] 4.1 Update `README.md` links and `uv run python` demo paths; fix sample file links to repository-relative paths
- [x] 4.2 Update `AGENTS.md` (and repository guidelines section if present) to describe `tests/examples/` for manual demos

## 5. Verification

- [x] 5.1 Run `uv run pytest -q` and fix any regressions
  - [x] 5.1.1 Found missing `tests/__init__.py` (task 3.1 was incomplete); file created
  - [x] 5.1.2 Found `uv run pytest -q` can't resolve `tests.examples.*` imports in `src/` layout; added `pythonpath = ["."]` in `pyproject.toml`
  - [x] 5.1.3 All 16 tests pass (`uv run pytest -q` and `uv run python -m pytest -q`)
