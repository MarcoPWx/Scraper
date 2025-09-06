---
title: ASR Cheatsheet
---

# ASR Cheatsheet

Copy-paste reminders for Automatic Speech Recognition integrations.

- Audio formats: 16kHz mono PCM (wav) is a safe default
- Chunking: 10–30s segments for streaming
- Timestamps: request word-level timestamps if downstream needs alignment
- Rate limits: respect vendor policies; add client backoff

