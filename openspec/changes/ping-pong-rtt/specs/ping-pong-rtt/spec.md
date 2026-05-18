## ADDED Requirements

### Requirement: Ping/Pong RTT measurement
The system SHALL support a Ping message from client to server containing the client's send timestamp (int64 milliseconds). The server SHALL reply with a Pong message that echoes the original timestamp.

#### Scenario: Successful RTT measurement
- **WHEN** a client sends a Ping message with its send timestamp
- **THEN** the server replies with a Pong message that includes the original timestamp
- **AND** the client computes RTT as the difference between receive time and the sent timestamp

### Requirement: Per-connection RTT storage
The system SHALL store the last measured RTT (in milliseconds) on the connection object and SHALL expose a getter to read the current RTT value.

#### Scenario: Query current RTT
- **WHEN** code calls connection.get_rtt_ms()
- **THEN** it returns the most recent RTT measured for that connection or null if none measured
