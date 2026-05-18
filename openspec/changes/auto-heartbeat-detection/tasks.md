## 1. Config 擴充

- [x] 1.1 `ClientConfig` 新增 `heartbeat_interval_sec: float = 5.0` 欄位
- [x] 1.2 `ServerConfig` 新增 `heartbeat_timeout_sec: float = 15.0` 欄位
- [x] 1.3 確認 frozen dataclass 相容性（現有使用方是否需調整）

## 2. Client 端心跳發送

- [x] 2.1 在 `ClientSocket.__init__` 中建立 `threading.Event` 作為心跳停止信號
- [x] 2.2 新增 `_heartbeat_loop` 方法：迴圈檢查 Event，每 `heartbeat_interval_sec` 發送一次 Heartbeat
- [x] 2.3 在 `Run()` 連線成功後啟動 `_heartbeat_loop` daemon thread
- [x] 2.4 在 `Stop()` 中設定 Event 信號，等待心跳 thread 結束
- [x] 2.5 Client 接收端（`_receive_messages`）保留既有的 Heartbeat 跳過邏輯（已實作 `continue`）

## 3. Server 端 Client 資訊儲存

- [x] 3.1 建立 `ClientInfo` 類別（`client_socket: socket`, `last_heartbeat_time: float`）
- [x] 3.2 將 `ServerSocket.__clients` 從 `list[socket.socket]` 改為 `dict[socket.socket, ClientInfo]`
- [x] 3.3 更新所有 `__clients` 存取處：accept 時加入 dict、斷線時從 dict 移除
- [x] 3.4 確保 `__clients_lock` 仍然保護所有 dict 存取

## 4. Server 端心跳處理與超時偵測

- [x] 4.1 在 `_handle_client` 中收到 Heartbeat 時：更新該 Client 的 `last_heartbeat_time`，並回傳 Pong（`SendMessages` with CONTROL/HEARTBEAT）
- [x] 4.2 Server 接收端保留既有的 Heartbeat 跳過邏輯（`continue`）— 但移到 timestamp 更新之後
- [x] 4.3 新增 `_heartbeat_timeout_checker` 方法：每秒掃描所有 Client，逾時則斷線清理
- [x] 4.4 在 `Run()` 啟動 `_heartbeat_timeout_checker` daemon thread
- [x] 4.5 在 `Stop()` 中停止 timeout checker thread

## 5. 測試

- [x] 5.1 撰寫 Client 心跳定時發送的單元測試（Config 預設值與自訂值）
- [x] 5.2 撰寫 Server 心跳接收與 Pong 回覆的單元測試（ServerConfig 心跳時間設定）
- [x] 5.3 撰寫 Server 心跳超時斷線的測試（ClientInfo 建立與時間記錄）
- [x] 5.4 執行 `uv run pytest -q -m "not integration"` — 21 passed ✓
