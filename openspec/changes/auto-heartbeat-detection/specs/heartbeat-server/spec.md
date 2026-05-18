## ADDED Requirements

### Requirement: Server tracks last heartbeat time per client
The ServerSocket SHALL track the last time each connected client sent a Heartbeat message.

#### Scenario: Heartbeat timestamp updated on receive
- **WHEN** ServerSocket receives a frame with (MainKind.CONTROL, SubKind.HEARTBEAT) from a client
- **THEN** the server SHALL update the last heartbeat timestamp for that client
- **THEN** the server SHALL silently consume the frame (not pass to `recvProtocol.recv_msg`)

#### Scenario: Initial heartbeat timestamp on connect
- **WHEN** a new client connects to the server
- **THEN** the server SHALL set the initial last heartbeat timestamp to the current time

### Requirement: Server replies to Heartbeat with Pong
The ServerSocket SHALL send a Pong response back to the client when a Heartbeat is received.

#### Scenario: Pong sent on Heartbeat
- **WHEN** ServerSocket receives a Heartbeat from a client
- **THEN** the server SHALL send a Pong frame (MainKind.CONTROL, SubKind.HEARTBEAT) back to that client

### Requirement: Server detects heartbeat timeout and disconnects client
The ServerSocket SHALL periodically check each client's last heartbeat timestamp, and disconnect any client whose last heartbeat exceeds `ServerConfig.heartbeat_timeout_sec`.

#### Scenario: Client disconnected on timeout
- **WHEN** a client's last heartbeat timestamp is older than `heartbeat_timeout_sec`
- **THEN** the server SHALL close that client's connection and remove it from the client list

#### Scenario: Active client not disconnected
- **WHEN** a client's last heartbeat timestamp is within `heartbeat_timeout_sec`
- **THEN** the server SHALL NOT disconnect that client

#### Scenario: Heartbeat timeout default value
- **WHEN** ServerConfig is created without specifying `heartbeat_timeout_sec`
- **THEN** `heartbeat_timeout_sec` SHALL default to 15.0 seconds

### Requirement: Heartbeat timeout checker runs on dedicated thread
The ServerSocket SHALL run a background thread that periodically checks for heartbeat timeouts.

#### Scenario: Heartbeat checker interval
- **WHEN** the heartbeat timeout checker thread is running
- **THEN** it SHALL check all clients for timeouts at least once per second

#### Scenario: Heartbeat checker stops on server stop
- **WHEN** `ServerSocket.Stop()` is called
- **THEN** the heartbeat timeout checker thread SHALL be stopped