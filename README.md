# Socket Package

一個可擴充的 TCP Socket 套件，內建最小核心協議，業務協議由使用者自行定義。

## 設計原則

- 套件內只保留「一定會用到」的核心協議：
  - `MainKind.CONTROL = 0`
  - `SubKind.STOP = 0`
  - `SubKind.HEARTBEAT = 1`
- 業務協議（例如聊天、遊戲、通知）請由使用者自行定義。
- 採用 frame 封包格式（長度前綴），可正確處理拆包/黏包。
- 訊息 header 固定為：`protocol_version + mainkind + subkind`。

## 安裝與開發

```bash
uv sync
uv run pytest -q
```

## 套件提供的核心 API

- `ClientSocket`, `ServerSocket`
- `ClientConfig`, `ServerConfig`
- `ProtocolRouter`
- `MainKind`, `SubKind`, `PROTOCOL_VERSION`（核心保留值）

## 快速開始

### 1. 定義你自己的協議

```python
from enum import IntEnum
from socket_package.Protocol.ProtocolKinds import MainKind as CoreMainKind
from socket_package.Protocol.ProtocolKinds import SubKind as CoreSubKind

class MainKind(IntEnum):
    CONTROL = int(CoreMainKind.CONTROL)   # 保留核心
    CHAT = 1001                           # 自定義

class SubKind(IntEnum):
    STOP = int(CoreSubKind.STOP)          # 保留核心
    HEARTBEAT = int(CoreSubKind.HEARTBEAT)# 保留核心
    SEND = 1                              # 自定義
```

### 2. 建立 Protocol Router

```python
from socket_package import MyByteArray
from socket_package.Protocol.RecvMsgProtocol import ProtocolRouter

class ClientProtocol(ProtocolRouter):
    def __init__(self, mgr):
        super().__init__()
        self._mgr = mgr
        self.register(MainKind.CONTROL, SubKind.STOP, self._on_stop)
        self.register(MainKind.CONTROL, SubKind.HEARTBEAT, self._on_heartbeat)
        self.register(MainKind.CHAT, SubKind.SEND, self._on_chat)

    def _on_stop(self, main_socket, msg: MyByteArray):
        self._mgr.stop()

    def _on_heartbeat(self, main_socket, msg: MyByteArray):
        return None

    def _on_chat(self, main_socket, msg: MyByteArray):
        print(msg.ReadStr())
```

### 3. 傳送訊息

```python
from socket_package import MyByteArray
from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION

payload = MyByteArray()
payload.WriteStr("hello")
client.SendMessages(client.mainSocket, MainKind.CHAT, SubKind.SEND, payload, protocol_version=PROTOCOL_VERSION)
```

### 4. 發送心跳

```python
from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION

client.SendHeartbeat(client.mainSocket, PROTOCOL_VERSION)
```

## 最小可跑範例（對齊目前專案）

已提供可直接執行的示範程式：

- [tests/ProtocolKinds.py](D:/Playground/SocketPackage/tests/ProtocolKinds.py)
- [tests/mainServer.py](D:/Playground/SocketPackage/tests/mainServer.py)
- [tests/mainClient.py](D:/Playground/SocketPackage/tests/mainClient.py)

啟動方式：

```bash
# Terminal 1
uv run python tests/mainServer.py

# Terminal 2
uv run python tests/mainClient.py
```

client 輸入指令：

- 一般文字：送出聊天訊息
- `HB`：送心跳
- `Stop`：送停止訊息並結束

## Config

```python
from socket_package import ClientConfig, ServerConfig

client_cfg = ClientConfig(
    host="127.0.0.1",
    port=9999,
    protocol_version=1,
    max_frame_size=1024 * 1024,
)

server_cfg = ServerConfig(
    host="0.0.0.0",
    port=9999,
    protocol_version=1,
    max_frame_size=1024 * 1024,
)
```

## 測試

目前測試涵蓋：

- frame 編解碼（含超長 frame 防護）
- protocol router（含未處理策略）
- message header（version + main/sub kind）
- config 注入與 sample protocol 路由

執行：

```bash
uv run pytest -q
```

## 核心類別

### ClientSocket
用戶端 Socket 類別，提供連線和通訊功能。

### ServerSocket
伺服器端 Socket 類別，提供監聽和通訊功能。

### FrameCodec
訊息框架編碼/解碼器，確保資料完整傳輸。

### MyByteArray
自定義位元組陣列類別，提供資料序列化功能。

## 通訊協定

套件支援多種通訊協定，定義在 `ProtocolKinds.py` 中：

- 控制訊息 (CONTROL)
- 資料訊息 (DATA)
- 心跳訊息 (HEARTBEAT)

## 配置選項

### ClientConfig
```python
ClientConfig(
    host='127.0.0.1',           # 伺服器位址
    port=8080,                  # 連接埠
    max_frame_size=1024*1024,   # 最大框架大小
    buffer_size=4096,           # 緩衝區大小
    retry_interval_sec=5,       # 重試間隔
    protocol_version=1          # 協定版本
)
```

### ServerConfig
```python
ServerConfig(
    host='0.0.0.0',             # 監聽位址
    port=8080,                  # 監聽連接埠
    max_frame_size=1024*1024,   # 最大框架大小
    buffer_size=4096,           # 緩衝區大小
    protocol_version=1          # 協定版本
)
```

## 錯誤處理

套件提供以下錯誤處理機制：

- 連線超時重試
- 框架大小超過限制
- 版本不匹配
- 通訊中斷偵測

## 開發

### 需求

- Python 3.13+
- uv 套件管理工具

### 安裝開發環境

```bash
uv sync
```

### 執行測試

```bash
pytest
```

## 貢獻

歡迎提交 issue 和 pull request 來改進這個套件。
