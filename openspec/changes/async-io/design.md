## Context

現有 `ClientSocket` 與 `ServerSocket` 使用 threading + blocking I/O，每個連線佔用一個 OS thread。對於遊戲伺服器需要同時處理大量連線的場景，asyncio 能提供更好的資源效率。

現有架構中，`FrameCodec`、`MyByteArray`、`ProtocolKinds` 都是純資料處理模組（無 blocking I/O），可直接重用。需要建立的是 async-aware 的 transport 層。

## Goals / Non-Goals

**Goals:**
- 建立 `AsyncClientSocket`：使用 `asyncio.open_connection()` 實作非阻塞 Client
- 建立 `AsyncServerSocket`：使用 `asyncio.start_server()` 實作非阻塞 Server
- 建立 `IAsyncRecvProtocol`：async 版本的 Protocol handler 介面
- 支援 `SendMessages()`、`BroadcastMessages()` 非同步版本
- 支援連線資料結構管理（連線列表、鎖保護）

**Non-Goals:**
- 修改現有同步版本的 `ClientSocket` / `ServerSocket`（保持向後相容）
- 自動心跳與斷線偵測（屬於 gap 1，在此版本不實作）
- Client ID / Session（屬於 gap 2）
- 房間/頻道管理（屬於 gap 3）

## Decisions

### 1. 獨立 async 模組，不繼承 TSocket
- **決策**：`AsyncClientSocket` 與 `AsyncServerSocket` 不繼承 `TSocket`，獨立實作
- **理由**：`TSocket` 的 `SendMessages()` 是同步 blocking 方法，與 async 模型衝突。重用邏輯會產生混亂的 sync/async 邊界
- **替代方案**：讓 `TSocket.SendMessages()` 同時支援 sync/async — 過度複雜，違反單一職責

### 2. 使用 `asyncio.StreamReader` / `StreamWriter`
- **決策**：使用 high-level `asyncio.open_connection()` / `asyncio.start_server()` 回傳的 `StreamReader`/`StreamWriter`
- **理由**：Python 官方推薦的高階 API，自動處理 buffer 與 flow control
- **替代方案**：使用 low-level `asyncio.Transport`/`Protocol` — 程式碼更複雜，對我們的需求來說 overkill

### 3. 建立獨立 `IAsyncRecvProtocol` 介面
- **決策**：新增 `async def recv_msg(...)` 的抽象類別，與同步版 `IRecvProtocol` 並存
- **理由**：async 版本的 handler 需要 `await` 支援，無法與同步版共用同一介面
- **替代方案**：在 `IRecvProtocol` 加入 `async def` 方法 — 會破壞所有現有實作

### 4. Server 使用 `list[asyncio.StreamWriter]` 管理連線
- **決策**：類似同步版的 list 結構，但存儲 `StreamWriter` 而非 `socket`
- **理由**：asyncio.start_server 的 callback 會收到 `(reader, writer)`，writer 是發送資料的端點
- **替代方案**：存儲 `(reader, writer)` tuple — 發送時只需要 writer

## Risks / Trade-offs

- **[Risk] 使用者需要在 async context 中操作**：呼叫方必須使用 `async def` 與 `await`。 → **Mitigation**：文件清楚標示 API 為 async
- **[Risk] 與同步版本 API 不一致**：`Run()` 變成 `await Run()`。 → **Mitigation**：保持方法名稱相同，僅加入 `async` 關鍵字
- **[Trade-off] 不共用 TSocket.SendMessages**：會有一些重複的 frame 編碼邏輯。 → 可抽取為獨立 utility function 或維持少許重複保持清晰