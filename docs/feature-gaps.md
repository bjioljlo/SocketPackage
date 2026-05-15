# SocketPackage 功能缺口清單

> 來源：Brainstorming session (2026-05-15)
> 場景：個人專案，遊戲伺服器用途

---

## 🔴 高優先 — 遊戲伺服器幾乎一定會需要

### 1. 🫀 自動心跳與斷線偵測
- 現狀：只有 `MySocket.SendHeartbeat()` 方法，但無自動定時發送機制
- 需求：
  - Client 端自動定時發送 Heartbeat（可設定間隔）
  - Server 端逾時沒收到 Heartbeat 時自動踢除連線
  - 可設定的逾時閾值

### 2. 🪪 連線身份 (Client ID / Session)
- 現狀：Server 只存 `list[socket]`，無法辨識每個連線的身份
- 需求：
  - 每個 Client 連線時自動分配唯一 ID
  - Server Socket 內部改用 dict 或物件儲存連線，而非單純的 list
  - 支援綁定玩家資料（如使用者名稱、角色等）

### 3. 🚪 房間/頻道管理 (Room / Lobby / Channel)
- 現狀：只有 `BroadcastMessages()` 全體廣播，無分組機制
- 需求：
  - 玩家可建立/加入/離開房間
  - 房間內的訊息只轉發給同房間成員
  - 支援創建者權限轉移

### 4. 🔄 非同步 I/O (asyncio)
- 現狀：使用 `threading.Thread` per connection 的 blocking I/O 模式
- 需求：
  - 提供 asyncio-based 的 ClientSocket / ServerSocket 實作
  - 對大量連線更省資源，避免 thread 開銷

---

## 🟡 中優先 — 有會更好

### 5. 🔒 TLS/SSL 加密
- 現狀：所有通訊皆為明碼
- 需求：
  - 支援 `ssl.wrap_socket()` 或 `context.wrap_socket()`
  - Config 中可選擇啟用 TLS 並指定憑證路徑

### 6. ⌛ Ping/Pong 延遲測量 (RTT)
- 現狀：Heartbeat 僅用於維持連線，無 RTT 計算
- 需求：
  - Client 記錄 Heartbeat 發送時間戳
  - Server 回傳 Pong 時附帶原始時間
  - 可查詢當前 RTT 值

### 7. 🔁 自動重連 (含 Exponential Backoff)
- 現狀：ClientSocket.Run() 固定 1 秒重試 (`retry_interval_sec`)
- 需求：
  - 改為指數退避（如 1s → 2s → 4s → 8s → 上限）
  - 可設定最大重連次數

### 8. 📝 Logging 系統取代 print()
- 現狀：全部使用 `print()` 輸出，無法控制 log 等級或輸出目標
- 需求：
  - 改用標準 `logging` 模組
  - 支援 DEBUG / INFO / WARNING / ERROR 等級
  - 可設定輸出到檔案或 stdout

---

## 🟢 低優先 — 架構擴展時再考慮

### 9. MyByteArray 序列化補全
- 現狀：支援 byte, str, int，缺少常用型別
- 需求：
  - 補上 `WriteFloat()`, `WriteDouble()`, `WriteBool()`
  - 對應的 `ReadFloat()`, `ReadDouble()`, `ReadBool()`

### 10. 🗄️ 物件池 (Object Pool) for MyByteArray
- 現狀：頻繁建立新 MyByteArray 物件
- 需求：
  - 提供簡單的物件池重用 bytearray 緩衝區
  - 減少 GC 壓力

### 11. 🐌 速率限制 (Rate Limiting)
- 現狀：無任何限流機制
- 需求：
  - 可設定每秒每個連線的最大訊息數/位元組數
  - 超過限制時可選擇丟棄或佇列延遲

### 12. 🎯 優雅斷線流程
- 現狀：`ServerSocket.Stop()` 直接發送 STOP 後關閉 socket，無等待
- 需求
  - 發送 STOP 後等待 Client 回應 ACK（可設 timeout）
  - 未回應再強制關閉

---

> 此清單將隨著實作進度更新，每完成一項請將其移至「已實作」區段或刪除該項目。