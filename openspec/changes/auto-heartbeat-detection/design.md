## Context

目前 `SocketPackage` 的心跳機制僅為手動呼叫 `MySocket.SendHeartbeat()`，Client 與 Server 皆無自動定時發送或超時偵測。連線管理中斷後，Server 無法自動清理僵死連線（zombie connections），造成資源浪費。

現有架構：
- `ClientSocket.Run()`：建立連線後啟動 `_receive_messages` 執行緒（blocking I/O）
- `ServerSocket.Run()`：Accept 連線後為每個 Client 啟動一個 `_handle_client` 執行緒
- 心跳封包目前僅在接收端被 `continue` 跳過（靜默捨棄），無任何雙向回應

## Goals / Non-Goals

**Goals:**
- Client 端以可設定間隔自動發送 Heartbeat 封包
- Server 端收到 Heartbeat 後回覆 Pong（沿用相同 SubKind.HEARTBEAT）
- Server 端追蹤每位 Client 的最後心跳時間，逾時則自動斷線清理
- 所有 Config 新增欄位皆可設定，且有合理的預設值
- 心跳定時器在 Client/Server Stop 時正確停止

**Non-Goals:**
- RTT 延遲測量（屬於獨立功能 #6）
- 非同步 I/O 支援（屬於獨立功能 #4）
- Client 端斷線重連（屬於獨立功能 #7）
- 修改既有公開 API 簽章（保持向後相容）

## Decisions

### 1. SubKind.HEARTBEAT 同時作為 Ping/Pong 使用
- **決策**：Client 送出的 Heartbeat 與 Server 回應的 Pong 使用相同的 `SubKind.HEARTBEAT`（值為 1）
- **理由**：現有 ProtocolKinds 已有定義 `HEARTBEAT = 1`，且 Client 與 Server 的接收端都已經有 `continue` 邏輯跳過此 SubKind，無需新增 SubKind 值
- **替代方案**：新增 `SubKind.PONG` — 會增加 protocol 變更複雜度，且需確保舊版相容性。維持單一 SubKind 更簡單且符合現有設計

### 2. 使用 threading.Timer 或 threading.Event 實現心跳定時器
- **決策**：Client 端使用 `threading.Thread` + `threading.Event` 的 loop 模式（類似現有 receive thread），而非 `threading.Timer`
- **理由**：`Timer` 無法在執行期間取消重排，且需處理 race condition。使用簡單的 while-not-event-loop 模式與現有程式碼風格一致
- **替代方案**：`threading.Timer` — 每次發送後需重新建立 Timer；`sched` module — 過於重量級

### 3. Server 使用 dict 取代 list 儲存 Client 資訊
- **決策**：將 `ServerSocket.__clients` 從 `list[socket.socket]` 改為 `dict[socket.socket, ClientInfo]`，其中 `ClientInfo` 為 dataclass 儲存 `last_heartbeat_time: float`
- **理由**：需要為每位 Client 關聯中繼資料（最後心跳時間），使用 dict 查詢更高效且語意清楚
- **替代方案**：使用 `list[tuple[socket, float]]` — 查詢效率差；使用平行 list — 維護複雜度高

### 4. Server 心跳超時檢查使用獨立執行緒
- **決策**：ServerSocket 啟動時建立一個專用背景執行緒，每秒掃描所有 Client 的最後心跳時間
- **理由**：不希望阻塞 Accept 循環或 Handle Client 執行緒；獨立執行緒職責單一
- **替代方案**：在 `_handle_client` 內部檢查 — 無法處理 Client thread 已掛掉的狀況

### 5. Client 端心跳執行緒的生命週期管理
- **決策**：心跳 thread 在 `ClientSocket.Run()` 成功建立連線後啟動，作為 daemon thread；在 `ClientSocket.Stop()` 時透過 Event 信號停止
- **理由**：daemon thread 確保即使 Client 異常退出也不會遺留執行緒；Event 機制提供乾淨的停止方式

### 6. 避免新增公開 API 介面
- **決策**：心跳定時啟動與超時處理皆封裝在 `ClientSocket` / `ServerSocket` 內部，不新增 `IRecvProtocol` 或 `ISocket` 的抽象方法
- **理由**：心跳是底層連線管理職責，不應暴露給上層 Protocol 開發者。保持 `IRecvProtocol` 簡潔

## Risks / Trade-offs

- **[Risk] 心跳執行緒與接收執行緒的 race condition**：`_receive_messages` 正在處理 Heartbeat Pong 的同時心跳 thread 可能正在發送新的 Heartbeat。 → **Mitigation**：Heartbeat 發送為無狀態單向操作，無需 lock；Pong 接收僅更新本地狀態時間戳，不涉及 shared state
- **[Risk] 多執行緒存取 `__clients` dict**：現有 `__clients_lock` 即可保護 dict 操作。 → **Mitigation**：心跳超時檢查 thread 需在每次迭代時取得 lock 後遍歷 dict
- **[Risk] Server 回應 Heartbeat 時 client 已斷線**：`SendMessages` 可能拋出異常。 → **Mitigation**：使用 try/except 包覆，斷線 client 由後續超時檢查清理
- **[Trade-off] 單一 SubKind.HEARTBEAT**：無法區分 Ping 與 Pong。 → 目前無此需求；若未來需要 RTT 測量可改用不同的 SubKind