## 1. IRecvProtocol 簽章更新（BREAKING CHANGE）

- [x] 1.1 `IRecvProtocol.recv_msg` 簽章新增 `client_id: int`
- [x] 1.2 `TRecvProtocol.recv_msg` 簽章新增 `client_id: int`
- [x] 1.3 `ProtocolHandler` 型別改為 `Callable[[socket, int, MyByteArray], None]`
- [x] 1.4 `ProtocolRouter.recv_msg` 傳遞 `client_id` 給 handler
- [x] 1.5 `ProtocolRouter.on_unhandled` 簽章新增 `client_id: int`

## 2. ServerSocket 改造

- [x] 2.1 建立 `ClientInfo`（`client_id`, `client_socket`, `last_heartbeat_time`, `player_data`）
- [x] 2.2 `__clients` 改為 `dict[int, ClientInfo]` + `_next_client_id` 計數器
- [x] 2.3 `Run()` accept 時分配 client_id，thread 帶入 client_id
- [x] 2.4 `_handle_client` 接收並傳遞 `client_id` 給 `recv_msg`
- [x] 2.5 新增 `get_client_info()` 與 `get_all_clients()`
- [x] 2.6 更新 `Stop()`、`BroadcastMessages()`、斷線清理

## 3. 測試與範例更新

- [x] 3.1 更新 `test_protocol_router.py` + 新增 `client_id` 傳遞測試
- [x] 3.2 更新 `tests/examples/` 中 Server/Client Protocol handler 簽章
- [x] 3.3 更新 `test_sample_protocol_routing.py` 傳入 `client_id`

## 4. 新增測試

- [x] 4.1 `test_client_id_auto_increment`
- [x] 4.2 `test_get_client_info_returns_none_for_invalid_id`
- [x] 4.3 `test_get_all_clients_returns_empty_dict`
- [x] 4.4 `test_client_info_player_data`（預設空 + 設/取值）

## 5. 驗證

- [x] 5.1 `uv run pytest -q` — 22 passed ✓
