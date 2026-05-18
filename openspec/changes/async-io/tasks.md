## 1. IAsyncRecvProtocol 介面

- [x] 1.1 新增 `IAsyncRecvProtocol` 抽象類別（`async def recv_msg(...)`）
- [x] 1.2 `__init__.py` 匯出 `IAsyncRecvProtocol` 與 `AsyncClientSocket`、`AsyncServerSocket`

## 2. AsyncClientSocket 實作

- [x] 2.1 新增 `AsyncClient/` 套件
- [x] 2.2 `Run()` 使用 `asyncio.open_connection()`
- [x] 2.3 receive loop：`FrameDecoder.feed()` + Heartbeat 跳過
- [x] 2.4 `SendMessages()`：編碼 frame 寫入 writer
- [x] 2.5 `Stop()` / `_close()`：關閉 writer，清理資源

## 3. AsyncServerSocket 實作

- [x] 3.1 新增 `AsyncServer/` 套件
- [x] 3.2 `Run()` 使用 `asyncio.start_server()`
- [x] 3.3 `_handle_client()` coroutine：解碼 + Heartbeat + 呼叫 protocol
- [x] 3.4 `SendMessages()`：寫入特定 client writer
- [x] 3.5 `BroadcastMessages()`：遍歷所有 writer
- [x] 3.6 `Stop()`：關閉 server + 所有 client writer

## 4. 測試

- [x] 4.1 AsyncClient + AsyncServer 整合測試：Client 發送訊息，Server 接收並轉發至 protocol handler
- [x] 4.2 新增 `pytest-asyncio` 依賴（`pyproject.toml` 設定 `asyncio_mode = "auto"`）

## 5. 驗證

- [x] 5.1 `uv run pytest -q -m "not integration"` — 14 passed ✓
- [x] 5.2 `uv run pytest -q tests/integration/test_async_io.py -v` — 1 passed ✓
