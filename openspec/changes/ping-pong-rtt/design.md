## Context

Current project has heartbeat support but no explicit RTT measurement. Game servers benefit from RTT metrics for matchmaking, lag compensation, and diagnostics.

## Goals / Non-Goals

**Goals:**
- Define message format for Ping/Pong and where to add handling.
- Implement RTT computation and expose a simple API on connections.
- Add tests that verify encoding/decoding and RTT calculation.

**Non-Goals:**
- Full telemetry pipeline or persistent metrics storage.
- Replacing heartbeat semantics (heartbeat remains for liveness).

## Decisions

- Use CONTROL main kind (existing) with new sub-kinds `PING=2`, `PONG=3` (add to ProtocolKinds). This keeps control messages grouped.
- Ping payload: 8-byte unix timestamp in milliseconds (int64) representing client send time. Pong echoes that timestamp back.
- RTT calculation: client records now()-sent_ts when Pong received; RTT = now - sent_ts.
- Store RTT (ms) as a float on connection metadata, update on each Pong.

## Risks / Trade-offs

[Risk] Clock skew between client and server could confuse absolute timestamps. ??Mitigation: Ping embeds client send time only for echo; RTT is computed solely by the originator using its own clock, so server clock accuracy is not required.

[Risk] Extra small messages increase bandwidth slightly. ??Mitigation: Messages are tiny and optional; disabled by default.

## Migration Plan

- Add ProtocolKinds entries and handlers; deploy with backward compatible defaults (Ping/Pong unused until client/servers opt in).

## Open Questions

- Should server optionally include server receipt timestamp in Pong? (Not required for RTT)
