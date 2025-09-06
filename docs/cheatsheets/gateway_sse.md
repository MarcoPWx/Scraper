---
title: Gateway & SSE Cheatsheet
---

# Gateway & SSE Cheatsheet

- SSE headers: Content-Type: text/event-stream; Cache-Control: no-cache
- Heartbeats: send comment lines periodically
- Reconnect: exponential backoff with last-event-id

