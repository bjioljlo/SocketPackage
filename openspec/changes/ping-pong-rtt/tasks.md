## 1. Setup

- [x] 1.1 Add ProtocolKinds entries for PING/PONG (non-breaking)
- [x] 1.2 Add minimal docs + examples in openspec change folder

## 2. Core Implementation

- [x] 2.1 Implement encoding/decoding for Ping/Pong payloads (int64 timestamp)
- [x] 2.2 Add ClientSocket.send_ping() helper that sends Ping with current timestamp
- [x] 2.3 Add ServerSocket handler to auto-respond Pong echoing timestamp
- [x] 2.4 Store and update connection.rtt_ms on Pong receipt (client-side)

## 3. Tests

- [x] 3.1 Unit test: Ping/Pong codec roundtrip
- [x] 3.2 Unit test: Client computes RTT correctly from synthetic timestamps
- [x] 3.3 Integration test (marked integration): client sends Ping, server replies Pong, client measures RTT > 0

## 4. Finalize

- [ ] 4.1 Update CHANGELOG / docs entry
- [ ] 4.2 Commit changes on feature/ping-pong-rtt branch
