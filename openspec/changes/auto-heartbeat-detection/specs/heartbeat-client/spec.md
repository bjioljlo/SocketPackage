## ADDED Requirements

### Requirement: Client auto-sends Heartbeat at configurable interval
The ClientSocket SHALL automatically send a Heartbeat message to the Server at a regular interval defined by `ClientConfig.heartbeat_interval_sec`.

#### Scenario: Heartbeat sent on schedule
- **WHEN** ClientSocket is connected and `heartbeat_interval_sec` is set to 5
- **THEN** a Heartbeat frame (MainKind.CONTROL, SubKind.HEARTBEAT) SHALL be sent every 5 seconds

#### Scenario: Heartbeat not sent when disconnected
- **WHEN** ClientSocket is not connected (`IsConnect` is False)
- **THEN** the automatic Heartbeat timer SHALL NOT send any Heartbeat

#### Scenario: Heartbeat interval default value
- **WHEN** ClientConfig is created without specifying `heartbeat_interval_sec`
- **THEN** `heartbeat_interval_sec` SHALL default to 5.0 seconds

### Requirement: Client handles Pong response from Server
The ClientSocket SHALL receive and process Pong responses from the Server without forwarding them to the user's `IRecvProtocol`.

#### Scenario: Pong received
- **WHEN** ClientSocket receives a frame with (MainKind.CONTROL, SubKind.HEARTBEAT)
- **THEN** the frame SHALL be silently consumed (not passed to `recvProtocol.recv_msg`)

#### Scenario: Pong does not interrupt heartbeat timer
- **WHEN** ClientSocket receives a Pong response
- **THEN** the heartbeat timer SHALL continue uninterrupted

### Requirement: Heartbeat stops when client stops
The automatic Heartbeat SHALL stop when `ClientSocket.Stop()` is called.

#### Scenario: Heartbeat stops on client stop
- **WHEN** `ClientSocket.Stop()` is called while Heartbeat timer is active
- **THEN** the Heartbeat timer SHALL be cancelled and no further Heartbeat SHALL be sent