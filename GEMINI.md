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
