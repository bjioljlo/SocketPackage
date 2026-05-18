## ADDED Requirements

### Requirement: AsyncServerSocket listens asynchronously
The AsyncServerSocket SHALL listen for incoming connections using `asyncio.start_server()` with configurable host, port, and backlog from `ServerConfig`.

#### Scenario: Server starts listening
- **WHEN** `await async_server.Run(protocol)` is called
- **THEN** the server SHALL bind to the configured host and port and start accepting connections

#### Scenario: Multiple concurrent clients
- **WHEN** multiple clients connect simultaneously
- **THEN** the server SHALL handle each client concurrently within the same event loop

### Requirement: AsyncServerSocket handles each client in a separate coroutine
Each connected client SHALL be handled by a dedicated coroutine that reads frames and dispatches messages to the async protocol handler.

#### Scenario: Client message dispatched with client info
- **WHEN** a client sends a valid frame
- **THEN** the server SHALL decode the frame and call `await recvProtocol.recv_msg(writer, main_kind, sub_kind, msg)`

#### Scenario: Heartbeat consumed silently
- **WHEN** a frame with (MainKind.CONTROL, SubKind.HEARTBEAT) is received
- **THEN** the server SHALL silently consume it without forwarding to the protocol handler

#### Scenario: Client disconnection handled
- **WHEN** a client disconnects
- **THEN** the handler coroutine SHALL exit cleanly and release resources

### Requirement: AsyncServerSocket sends messages
The AsyncServerSocket SHALL provide `SendMessages()` for sending framed messages to a specific client via its writer.

#### Scenario: Send message to client
- **WHEN** `send_messages(writer, main_kind, sub_kind, msg)` is called
- **THEN** the message SHALL be encoded as a frame and written to the client's transport

### Requirement: AsyncServerSocket broadcasts to all clients
The AsyncServerSocket SHALL provide `BroadcastMessages()` for sending a message to all connected clients, with an option to exclude the sender.

#### Scenario: Broadcast to all clients
- **WHEN** `broadcast_messages(sender_writer, main_kind, sub_kind, msg)` is called
- **THEN** the message SHALL be sent to all connected clients except the sender

#### Scenario: Broadcast with sendSelf=True
- **WHEN** `broadcast_messages(sender_writer, main_kind, sub_kind, msg, sendSelf=True)` is called
- **THEN** the message SHALL be sent to all connected clients including the sender

### Requirement: AsyncServerSocket stops gracefully
The AsyncServerSocket SHALL support graceful shutdown that closes the server and all client connections.

#### Scenario: Stop closes all connections
- **WHEN** `stop()` is called
- **THEN** the server SHALL close the listening socket and all active client connections