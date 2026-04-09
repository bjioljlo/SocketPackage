# Repository Guidelines

## Project Structure & Module Organization
核心套件程式碼位於 `src/socket_package/`。主要公開模組分為 `Client/`、`Server/` 與 `Protocol/`，分別負責 socket 抽象層、client/server 進入點，以及 frame 與 protocol 相關工具。測試與可執行範例放在 `tests/`；檔名為 `test_*.py` 的檔案屬於自動化測試，`mainServer.py` 與 `mainClient.py` 則是手動整合示範。專案中繼資料定義於 `pyproject.toml`，而 `README.md` 說明公開 API 與使用方式。

## Build, Test, and Development Commands
使用 `uv` 進行環境管理與指令執行。

- `uv sync`: install runtime and dev dependencies from `pyproject.toml` and `uv.lock`.
- `uv run pytest -q`: run the full automated test suite quietly.
- `uv run python tests/mainServer.py`: start the sample server.
- `uv run python tests/mainClient.py`: start the sample client in a second terminal.

請從 repository root 執行上述指令，確保 `src/` 結構下的 import 能正確解析。

## Coding Style & Naming Conventions
遵循現有 Python 風格：使用 4 個空白縮排、在合適處補上 type hints，並維持模組小而聚焦。函式、method、變數與測試名稱使用 `snake_case`；類別名稱使用 `PascalCase`，例如 `FrameDecoder`、`ClientSocket`。與 protocol 相關的常數或 enum 成員應保持語意清楚且穩定；本專案現有慣例包含 `PROTOCOL_VERSION`、`CONTROL`、`HEARTBEAT` 等全大寫命名。

目前 `pyproject.toml` 尚未設定 formatter 或 linter，因此提交變更時請以周邊既有程式風格為準，避免夾帶無關的格式調整。

## Testing Guidelines
測試採用 `pytest`。新增測試時請放在 `tests/test_*.py`，並以行為描述作為測試名稱，例如 `test_send_messages_writes_header_and_payload_in_frame`。建議優先補足 frame 編解碼、routing 與 config 行為的快速單元測試，再視需要補充 socket 層級的整合案例。提交 PR 前請先執行 `uv run pytest -q`。

## Commit & Pull Request Guidelines
近期 commit 紀錄採用 Conventional Commit 前綴，例如 `feat:`、`refactor:`、`chore:`。commit subject 請保持簡短並使用祈使語氣，例如 `feat: add heartbeat timeout handling`。PR 內容應說明行為變更、標註是否影響 protocol 或 API、在可行時附上相關 issue，只有當變更會影響可執行範例或開發流程時，才需要附上 terminal 輸出或畫面截圖。

## Configuration Notes
此套件要求 Python 3.13 以上版本。請讓 sample config 與 protocol 範例持續對齊 `SocketConfig.py` 與 `ProtocolKinds.py` 中的預設值，避免文件、示範程式與測試之間出現落差。
