## Context

ServerSocket 目前使用 `list[socket.socket]` 管理連線，無法辨識每個連線的身份。`IRecvProtocol.recv_msg()` 收到訊息時只知道是哪個 socket，無法得知是哪個玩家。上層 protocol handler 無法綁定玩家資料。

## Goals / Non-Goals

**Goals:**
- Server 自動分配遞增唯一 Client ID
- `__clients` 從 `list[socket]` 改為 `dict[int, ClientInfo]`（以 client_id 為 key）
- `ClientInfo` 支援 `player_data: dict` 綁定任意玩家資料
- `IRecvProtocol.recv_msg()` 簽章新增 `client_id: int` 參數
- `ProtocolRouter` 傳遞 client_id 給註冊的 handler
- ServerSocket 提供 `get_client_info()` 與 `get_all_clients()` 查詢 API

**Non-Goals:**
- Client 連線後從 Server 接收 client_id 的通知（屬於獨立功能，暫不實作）
- 房間/頻道管理（屬於 gap 3）
- 修改 ClientSocket 的公開 API（僅 ServerSocket 端變更）

## Decisions

### 1. `__clients` 改為 `dict[int, ClientInfo]`
- **決策**：以 `client_id`（遞增整數）為 key，取代現有 `list[socket.socket]`
- **理由**：設計與 gap 1 的方向一致。用整數 ID 查詢比用 socket object 查詢更穩定（socket 重連後會變）
- **替代方案**：保留 list + 平行 `dict[int, socket]` — 維護複雜度高

### 2. `ClientInfo` 加入 `client_id` 與 `player_data`
- **決策**：新增欄位 `client_id: int` 與 `player_data: dict[str, Any]`
- **理由**：`player_data` 讓上層自由綁定使用者名稱、角色 ID 等，不需要預先定義 schema
- **替代方案**：用 `ProtocolRouter` 自行管理玩家資料 — 增加上層負擔，且無法與 ServerSocket 的生命週期掛鉤

### 3. `IRecvProtocol.recv_msg` 簽章新增 `client_id: int`
- **決策**：在 `mainSocket` 之後插入 `client_id` 參數
- **理由**：這是唯一的 source of truth — ServerSocket 知道是哪個 client 送來的訊息
- **衝擊**：這是 **BREAKING CHANGE**，所有實作 `IRecvProtocol` 的類別都需要更新
- **遷移策略**：同時更新 `TRecvProtocol`、`ProtocolRouter`、所有測試與範例

### 4. `ProtocolRouter` 註冊 handler 簽章更新
- **決策**：`ProtocolHandler` 從 `Callable[[socket, MyByteArray], None]` 改為 `Callable[[socket, int, MyByteArray], None]`，第二個參數為 `client_id`
- **理由**：保持一致，讓 handler 在不知道 socket 的情況下也能辨識是哪個 client
- **替代方案**：handler 自行從 socket 查找 client_id — 增加重複程式碼

### 5. Client 端不主動接收 client_id 通知
- **決策**：此版本不實作 Server → Client 的 ID 通知機制
- **理由**：目前的 feature-gap 需求重點在 Server 端能辨識連線身份。Client 知道自己 ID 的好處較少
- **非目標**：若未來需要 Client 也知道自己的 ID，可在連線完成後由 Server 發送 CONTROL 訊息

## Risks / Trade-offs

- **[Risk] Breaking change 影響範圍大**：`IRecvProtocol` 修改後，所有現有實作（`TRecvProtocol`、`ProtocolRouter`、範例、測試）都需修改。 → **Mitigation**：一次性修改所有引用處，確保 compile-time 即發現所有問題
- **[Risk] dict key 從 socket 改為 int 需注意 hash 安全性**：socket object 無法作為 stable key（重連後會變）。 → **Mitigation**：使用 int（client_id）作為 key，socket 作為屬性存在 `ClientInfo` 中
- **[Trade-off] player_data 為 dict 無型別安全**：上層可自由塞入任何型別。 → 不強制加 dataclass 或 TypedDict，保持靈活性