## ADDED Requirements

### Requirement: Server auto-assigns unique client ID on connect
The ServerSocket SHALL assign a unique, auto-incrementing integer ID to each newly connected client.

#### Scenario: Client receives unique ID
- **WHEN** a new client connects to the server
- **THEN** the client SHALL be assigned a unique ID that no other currently connected client has

#### Scenario: IDs are monotonically increasing
- **WHEN** clients connect sequentially
- **THEN** each new client SHALL receive an ID greater than the previous one

### Requirement: IRecvProtocol receives client_id
The `IRecvProtocol.recv_msg()` method SHALL include the `client_id: int` parameter so protocol handlers can identify the sender.

#### Scenario: Protocol handler receives client_id
- **WHEN** ServerSocket dispatches a received message to `recvProtocol.recv_msg()`
- **THEN** the `client_id` parameter SHALL be the ID of the client that sent the message

#### Scenario: ProtocolRouter passes client_id to handler
- **WHEN** `ProtocolRouter.recv_msg()` is called with a valid `client_id`
- **THEN** the registered handler function SHALL receive `client_id` as the second parameter (after `mainSocket`)

### Requirement: Server exposes client lookup API
The ServerSocket SHALL provide methods for external query of connected clients.

#### Scenario: get_client_info returns client data
- **WHEN** `get_client_info(client_id)` is called with an existing client ID
- **THEN** it SHALL return the `ClientInfo` object for that client

#### Scenario: get_client_info returns None for invalid ID
- **WHEN** `get_client_info(client_id)` is called with a non-existent ID
- **THEN** it SHALL return `None`

#### Scenario: get_all_clients returns all connected clients
- **WHEN** `get_all_clients()` is called
- **THEN** it SHALL return a dict mapping `client_id` to `ClientInfo` for all connected clients

### Requirement: ClientInfo supports player data binding
The `ClientInfo` object SHALL support attaching arbitrary player metadata.

#### Scenario: Set player data on ClientInfo
- **WHEN** external code sets `client_info.player_data["username"] = "Alice"`
- **THEN** the data SHALL be accessible via the same key

#### Scenario: Default player_data is empty
- **WHEN** a new `ClientInfo` is created
- **THEN** `player_data` SHALL be an empty dict