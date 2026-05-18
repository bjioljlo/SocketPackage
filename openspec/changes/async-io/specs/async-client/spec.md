## ADDED Requirements

### Requirement: AsyncClientSocket establishes connection asynchronously
The AsyncClientSocket SHALL connect to a server using `asyncio.open_connection()` with configurable host and port from `ClientConfig`.

#### Scenario: Successful async connection
- **WHEN** `await async_client.Run(protocol)` is called with a reachable server
- **THEN** the client SHALL establish a connection and start receiving messages

#### Scenario: Connection refused handled gracefully
- **WHEN** the server is unreachable
- **THEN** the connect attempt SHALL raise an appropriate exception without crashing the event loop

### Requirement: AsyncClientSocket reads messages asynchronously
The AsyncClientSocket SHALL read incoming data from the transport using `await reader.read()` and dispatch decoded frames to the async protocol handler.

#### Scenario: Message received and dispatched
- **WHEN** a valid frame is received from the server
- **THEN** the client SHALL decode the frame and call `await recvProtocol.recv_msg(mainSocket, main_kind, sub_kind, msg)`

#### Scenario: Heartbeat silently consumed
- **WHEN** a frame with (MainKind.CONTROL, SubKind.HEARTBEAT) is received
- **THEN** the client SHALL silently consume it without forwarding to the protocol handler

#### Scenario: Connection closed by server
- **WHEN** the server closes the connection
- **THEN** the receive loop SHALL exit gracefully

### Requirement: AsyncClientSocket sends messages asynchronously
The AsyncClientSocket SHALL provide `SendMessages()` for sending framed protocol messages over the established connection.

#### Scenario: Send framed message
- **WHEN** `send_messages(main_kind, sub_kind, msg)` is called
- **THEN** the message SHALL be encoded as a frame (length prefix + protocol header + payload) and written to the transport

### Requirement: AsyncClientSocket stops cleanly
The AsyncClientSocket SHALL support graceful shutdown via a `Stop()` method that closes the transport and cleans up resources.

#### Scenario: Stop closes connection
- **WHEN** `stop()` is called
- **THEN** the transport SHALL be closed and no further messages SHALL be sent or received