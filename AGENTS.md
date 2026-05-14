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

## 專案概觀 (Project Overview)

本儲存庫為 **Python 套件 `socket_package`**：提供 socket 抽象層、client／server 進入點，以及 frame 與 protocol 相關工具，供應用程式或服務整合自訂訊息框架與連線行為。性質為**函式庫**；`tests/` 內含自動化測試與手動整合示範程式。

### 核心技術 (Core Technologies)

- **語言：** Python（`requires-python` 為 `>=3.13`，以 `pyproject.toml` 與（若存在）`.python-version` 為準）
- **套件與環境管理：** [`uv`](https://docs.astral.sh/uv/)（`pyproject.toml`、`uv.lock`）
- **測試：** `pytest`（開發依賴定義於 `pyproject.toml` 的 `[dependency-groups]` → `dev`）
- **建置後端：** `uv_build`（見 `pyproject.toml` 的 `[build-system]`）
- **靜態檢查／格式化：** 目前 `pyproject.toml` 未設定 ruff、mypy 等；提交變更時請以周邊既有程式風格為準，避免夾帶無關的格式調整
- **規格：** [OpenSpec](https://github.com/Fission-AI/OpenSpec)（`openspec/`，與 SDD 流程搭配）

### 系統架構 (Architecture)

- **`src/socket_package/`**：核心實作；公開模組大致分為 `Client/`、`Server/`、`Protocol/`（socket 抽象、進入點、frame／protocol 工具）
- **`tests/`**：測試與示範；`test_*.py` 為自動化測試，`mainServer.py` 與 `mainClient.py` 為手動整合示範
- **`openspec/`**：OpenSpec 設定與規格／變更產物（`config.yaml`、主規格 `specs/`、進行中變更 `changes/`、封存 `changes/archive/` 等）
- **`README.md`**：安裝、使用方式與公開 API 摘要
- **`pyproject.toml`**：專案中繼資料、相依性、建置與工具設定
- **`uv.lock`**：鎖定解析後相依性（應納入版本控制）

## 專案結構與模組配置

採 **`src/` 版面**，從 repository root 執行指令，確保匯入解析到已安裝的套件而非工作目錄下同名的誤用路徑。

### 目錄結構

- `src/socket_package/`：套件原始碼
- `tests/`：單元／整合測試與可執行示範
- `openspec/`：OpenSpec（`config.yaml`、`specs/`、`changes/` 等；CLI 與代理流程見 `.cline/skills/`、`.clinerules/workflows/`）
- `pyproject.toml`、`uv.lock`：專案與鎖檔
- `.gitignore`：忽略 `__pycache__/`、`.venv/`、建置產物等

## 建置、測試與開發指令（uv）

在**專案根目錄**執行；代理或鏡像設定依本機環境調整。

### 環境與相依性

- `uv sync`：依 `uv.lock` 建立／更新虛擬環境並安裝專案與預設群組（含開發依賴；若環境使用 `UV_NO_DEV` 等，請改以 `uv sync --group dev` 或 `uv sync --all-groups` 等，以所用 uv 版本說明為準）
- `uv lock`：更新鎖檔（新增或變更依賴後應執行並提交 `uv.lock`）
- `uv add <套件>`：新增執行期依賴並更新鎖檔
- `uv add --dev <套件>`：新增開發依賴（實際旗標以所用 `uv` 版本文件為準）

### 在專案環境中執行指令

- `uv run pytest -q`：執行完整自動化測試（精簡輸出）
- `uv run python tests/mainServer.py`：啟動示範 server
- `uv run python tests/mainClient.py`：於另一終端機啟展示範 client
- `uv run python -m <module>`：執行其他模組或入口（依需求）

### 本機無 uv 時的後備方式

若僅有已啟用的 venv 與已安裝的依賴：

- `python -m pytest`
- `pip install -e .`：以 editable 安裝目前套件，便於開發時匯入

### 模組設計原則

- 公開 API 盡量穩定、邊界清楚；內部實作可以子模組或命名慣例隔離
- 避免循環依賴與過大的「萬用」模組；職責單一、可測試為優先

## 程式風格與命名慣例

- **縮排：** 4 個空格
- **命名：** 模組／函式／變數／測試使用 `snake_case`；類別 `PascalCase`（例如 `FrameDecoder`、`ClientSocket`）
- **常數與 enum：** 與 protocol 相關者應語意清楚且穩定；現有慣例包含 `PROTOCOL_VERSION`、`CONTROL`、`HEARTBEAT` 等全大寫命名
- **型別提示：** 公開介面與非顯而易見的邏輯建議標註
- **簡潔：** 優先可讀與可維護；模組維持小而聚焦

## 測試指南

- **位置：** `tests/`
- **命名：** `test_*.py`；測試函式名稱應描述行為與預期，例如 `test_send_messages_writes_header_and_payload_in_frame`
- **涵蓋：** 建議優先補足 frame 編解碼、routing 與 config 的單元測試，再視需要補充 socket 層級整合案例
- **Bug 修復：** 應附回歸測試；理想上先寫失敗測試再修正實作（TDD）
- **提交前：** 執行 `uv run pytest -q`

## 開發流程規範

功能開發建議依下列順序，與 **SDD（規格驅動開發）** 及 **TDD（測試驅動開發）** 對齊：

1. **規格先行：** 於 **OpenSpec** 流程中撰寫或更新規格與變更紀錄（見下節），明確需求、API／行為與邊界案例
2. **測試依規格：** 依規格撰寫或更新測試，使測試足以驗證規格
3. **實作：** 撰寫程式直至測試通過，避免「先實作再補規格」造成漂移
4. **驗證與提交：** 確認實作與規格一致後，再進行 commit／PR

執行測試與靜態檢查時，優先使用 **`uv run …`**，以與鎖檔及 CI 一致。

## Commit 與 Pull Request 指南

- **Commit 訊息：** 建議遵循 [Conventional Commits](https://www.conventionalcommits.org/)（例如 `feat:`、`fix:`、`refactor:`、`chore:`、`docs:`）；subject 簡短、祈使語氣，例如 `feat: add heartbeat timeout handling`
- **分支：** 使用可辨識目的的名稱（例如 `feat/...`、`fix/...`）
- **Pull Request：** 說明行為變更與動機、標註是否影響 **protocol** 或 **公開 API**、在可行時附上相關 issue；僅當變更影響可執行範例或開發流程時，才需要附上終端輸出或畫面截圖；若影響安裝／使用方式，請同步更新 `README.md` 或官方文件；與 OpenSpec 相關的變更請在 PR 中對應說明規格／提案／任務的更新範圍

## OpenSpec 工作流說明

本專案以 **OpenSpec** 管理規格與變更，建議依下列階段進行：

1. **Explore** — 探索需求、釐清問題與規格
2. **Propose** — 提出變更提案（設計、API、任務拆解）
3. **Apply** — 依規格與任務實作
4. **Archive** — 完成後封存變更紀錄

相關目錄為 **`openspec/`**：

- **`config.yaml`**：OpenSpec 專案設定（例如 `schema: spec-driven`）
- **`specs/<capability>/spec.md`**：能力主規格
- **`changes/<name>/`**：進行中的變更（常見產物含 `proposal.md`、`design.md`、`tasks.md`、delta `specs/` 與 `.openspec.yaml`）；完成後可移至 `changes/archive/`

日常操作仰賴 **`openspec` CLI**（例如 `openspec list`、`openspec new change`、`openspec status`）；與 Explore／Propose／Apply／Archive 對應的細步驟見 **`.clinerules/workflows/`** 與 **`.cline/skills/openspec-*`**。進行會影響對外行為或 protocol 的變更時，應讓 OpenSpec 產物與程式碼、測試一併演進，避免規格與實作脫節。

## 設定與範例對齊（Configuration Notes）

此套件要求 **Python 3.13 以上**。請讓 sample config 與 protocol 範例持續對齊下列檔案中的預設值，避免文件、示範程式與測試之間出現落差：

- `src/socket_package/Protocol/SocketConfig.py`
- `src/socket_package/Protocol/ProtocolKinds.py`

## 貢獻補充說明

- 範例與測試中的 `import` 路徑應與**實際發佈的套件名稱**一致（例如 `socket_package`），避免依賴未安裝的相對路徑技巧
- 新增依賴後請執行 **`uv lock`**（或等效流程）並將 **`uv.lock`** 一併提交，除非儲存庫政策另有規定

---

與 `uv` 相關的子命令請以 [官方文件](https://docs.astral.sh/uv/) 與本機鎖定的 `uv` 版本為準。
