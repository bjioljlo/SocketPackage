## Why

遊戲伺服器需要穩定的長連線機制。目前僅有手動 `SendHeartbeat()` 方法，缺乏自動定時發送與超時斷線偵測，導致無法及時發現僵死連線（zombie connections），浪費伺服器資源。

## What Changes

- **Client 自動心跳發送**：新增可設定的定時器，自動向 Server 發送 Heartbeat 封包
- **Server 心跳超時偵測**：Server 追蹤每個 Client 最後收到 Heartbeat 的時間，逾時未收到則自動踢除連線
- **Server 回應 Heartbeat**：Server 收到 Heartbeat 後回覆 Pong 給 Client（類似 Ping/Pong 機制）
- **可設定的心跳間隔與超時閾值**：在 `ClientConfig` 與 `ServerConfig` 中新增對應欄位

## Capabilities

### New Capabilities
- `heartbeat-client`: Client 端自動定時發送 Heartbeat，並接收 Server 回覆的 Pong 以確認連線健康
- `heartbeat-server`: Server 端追蹤每位 Client 的心跳時間，逾時未收到時自動斷線清理

### Modified Capabilities
- (無，此為全新功能，不修改既有規格)

## Impact

- **`ClientSocket.py`**：新增心跳定時器執行緒與 Pong 接收邏輯
- **`ServerSocket.py`**：新增心跳超時監控告、Client 連線清理邏輯
- **`ServerSocket.__clients`**：需擴充儲存每位 Client 的最後心跳時間
- **`SocketConfig.py`**：`ClientConfig` 新增 `heartbeat_interval_sec`；`ServerConfig` 新增 `heartbeat_timeout_sec`
- **`ProtocolKinds.py`**：需確認 SubKind 有 `PONG`（或直接沿用 HEARTBEAT 作為雙向信令）
- 無新增外部 dependency