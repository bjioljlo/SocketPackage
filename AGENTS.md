# SocketPackage - 專案上下文與指南

## 專案概觀
`SocketPackage` 是一個模組化且具擴充性的 Python 3.13+ TCP Socket 函式庫。它提供了一個構建網路應用程式的核心框架，專注於自定義 Protocol 定義，同時處理底層網路問題，如訊息 Framing（拆包與黏包處理）。

### 核心技術
- **Python 3.13+**: 主要開發語言。
- **uv**: 依賴管理與執行工具。
- **pytest**: 測試框架。
- **標準函式庫 `socket`**: 基礎網路實作。

### 架構
- **Framing**: 使用 4 位元組長度前綴的 Frame 格式（透過 `FrameCodec`），以處理 TCP 串流問題（封包拆分/合併）。
- **Protocol 結構**: 每個訊息 Header 包含 `protocol_version (1B) + main_kind (1B) + sub_kind (1B)`。
- **序列化 (Serialization)**: `MyByteArray` 提供了一個自定義介面，用於在 Byte Buffer 中讀取和寫入原始型別。
- **路由 (Routing)**: `ProtocolRouter` 允許為特定的 `(main_kind, sub_kind)` 配對註冊 Handler。
- **組件**:
  - `ClientSocket` / `ServerSocket`: TCP 連線的高階封裝。
  - `SocketConfig`: 用於設定 Timeout、Buffer Size 和 Max Frame Size。

## 建置與執行

### 設定
確保已安裝 `uv`，然後同步環境：
```bash
uv sync
```

### 執行測試
使用 `pytest` 執行測試套件：
```bash
uv run pytest
```
*注意：使用 `-q` 取得簡約輸出，或使用 `-v` 取得詳細輸出。*

### 執行範例
若要查看套件運行狀況，請執行位於 `tests` 目錄中的範例 Server 和 Client：
1. **啟動 Server**: `uv run python tests/mainServer.py`
2. **啟動 Client**: `uv run python tests/mainClient.py`

## 開發規範

### Protocol 定義
- **保留核心種類 (Reserved Core Kinds)**: `MainKind.CONTROL (0)` 保留給套件核心功能，如 `HEARTBEAT (1)` 和 `STOP (0)`。
- **自定義種類 (Custom Kinds)**: 使用者定義的 Protocol 應從 `1001` 或其他較大數值開始，以避免與未來的核心更新發生衝突。
- **註冊**: 務必使用 `ProtocolRouter.register()` 或 `@router.route(main, sub)` 裝飾器來處理傳入訊息。

### 編碼標準
- **型別提示 (Type Hinting)**: 在整個程式碼庫中使用 Python Type Hints。
- **序列化**: 務必使用 `MyByteArray` 進行資料 Payload 的序列化，以確保全網路的一致性。
- **Buffer 安全**: 注意 `SocketConfig` 中的 `max_frame_size`，以防止因超大封包導致的記憶體耗盡。

### 測試
- 新功能應在 `tests/` 目錄中包含單元測試。
- 特別針對邊際情況（空 Payload、大型 Payload）驗證 Frame 的編解碼。

## 專案結構
- `src/socket_package/`: 核心函式庫原始碼。
  - `Client/`: 用戶端連線邏輯。
  - `Server/`: 伺服器端監聽與連線管理。
  - `Protocol/`: 訊息傳遞、Framing 與路由邏輯。
- `tests/`: 單元測試與可執行的示範腳本。
- `openspec/`: 實驗性變更管理與規格說明。

---

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

## 開發流程準則

### SDD (Specification Driven Development) 規格導向開發
1. **先寫規格再實作**: 任何功能變更前，先在 `openspec/` 建立對應的規格文件，定義行為、邊界條件與預期結果
2. **公開 API 優先**: 優先設計外部介面與合約，再實作內部邏輯
3. **文件與程式同步**: 規格文件、程式註解與實際程式碼必須保持一致
4. **邊界條件定義**: 明確定義成功、失敗與例外狀況的處理行為

### TDD (Test Driven Development) 測試導向開發
1. **測試優先**: 實作功能前先撰寫對應的單元測試，確保測試一開始是失敗狀態
2. **最小實作**: 只撰寫剛好能通過目前測試的程式碼，不做過度設計
3. **重構循環**: 通過測試後再進行重構，確保每次重構後所有測試依然通過
4. **測試涵蓋原則**:
   - 所有公開方法必須有對應測試
   - 邊界條件、例外狀況必須被測試覆蓋
   - Protocol 定義與 Frame 編解碼必須有 100% 測試覆蓋率
5. **整合測試**: 核心功能完成後必須補充對應的整合測試案例

## Configuration Notes
此套件要求 Python 3.13 以上版本。請讓 sample config 與 protocol 範例持續對齊 `SocketConfig.py` 與 `ProtocolKinds.py` 中的預設值，避免文件、示範程式與測試之間出現落差。
