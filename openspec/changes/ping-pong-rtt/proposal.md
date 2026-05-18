## Why

Networked games need latency visibility. This change adds a lightweight Ping/Pong RTT measurement so clients and servers can measure round-trip time for connections and expose a current RTT metric.

## What Changes

- Add new capability `ping-pong-rtt` to send Ping messages and reply with Pong.
- Store per-connection RTT in server/client connection metadata and expose a query API.
- Add unit and integration tests covering encoding, decoding, and RTT computation.

## Capabilities

### New Capabilities
- `ping-pong-rtt`: Measure and expose per-connection Round-Trip Time (RTT). Client sends Ping with timestamp; server echoes Pong with original timestamp.

### Modified Capabilities
- (none)

## Impact

Affected code:
- src\socket_package\Protocol\ProtocolKinds.py (add PING/PONG control sub-kinds)
- src\socket_package\Client\ClientSocket.py (send_ping(), rtt storage)
- src\socket_package\Server\ServerSocket.py (auto-respond Pong, store rtt)
- tests/ (new unit + integration tests)
