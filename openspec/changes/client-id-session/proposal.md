## Why

Server 目前使用 `list[socket.socket]` 管理連線，無法辨識每個連線的身份。Protocol handler 收到訊息時只能拿到 raw socket，無法區分是哪個玩家，也無法綁定玩家資料（如使用者名稱、角色等）。遊戲伺服器需要能識別每個 Client 的身份。

## What Changes

- **自動分配 Client ID**：Server 在每個 Client 連線時自動產生唯一 ID（遞增整數）
- **ClientInfo 擴充**：現有 `ClientInfo` 概念（從 gap 1 的 `__clients: dict` 設計出發）加入 `client_id` 與可選的 `player_data: dict`，讓上層綁定任意玩家資料
- **ServerSocket 內部改用 dict 儲存**：`list[socket]` → `dict[int, ClientInfo]`，以 client_id 為 key
- **暴露 `get_client_info(client_id)`** 與 `get_all_clients()` 方法供外部查詢
- **IRecvProtocol 接收 client_id**：`recv_msg` 簽章加入 `client_id` 參數，讓 protocol handler 可直接識別發送者

## Capabilities

### New Capabilities
- `client-identity`: Client 連線時自動分配唯一 ID，ServerSocket 提供查詢與綁定玩家資料的能力

### Modified Capabilities
- 無（此為全新功能，不修改既有規格）

## Impact

- **`ServerSocket.py`**：`__clients` 改為 `dict[int, ClientInfo]`，新增 `_next_client_id` 計數器，新增 `get_client_info()`、`get_all_clients()` 方法
- **`RecvMsgProtocol.py`**：`IRecvProtocol.recv_msg` 簽章新增 `client_id: int` 參數 — **BREAKING CHANGE**
- **所有實作 `IRecvProtocol` 的地方**：需更新 `recv_msg` 簽章（`tests/examples/`、`tests/integration/`）
- **`ClientSocket.py`**：Client 端連線後從 Server 接收分配到的 client_id（透過 CONTROL 訊息通知）
- 無新增外部 dependency