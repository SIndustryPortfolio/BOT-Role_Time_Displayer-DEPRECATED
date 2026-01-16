# Game Event Logging & Management API

A Python-based web API built with :contentReference[oaicite:0]{index=0} that handles **game event logging, moderation tracking, automation tasks, and database operations**.  
Designed to integrate with external game systems (such as :contentReference[oaicite:1]{index=1}) and Discord-based infrastructure.

---

## Overview

This project acts as a **central backend service** for:
- Logging gameplay and moderation events
- Managing player data (bans, warns, tryouts, purchases)
- Triggering scheduled maintenance tasks
- Relaying events to external webhook systems (e.g. Discord)

It exposes a REST-style API secured via an **authentication token** and runs background jobs using a scheduler.

---

## Key Features

- 🌐 REST API built with Flask
- 🗄️ Database integration via :contentReference[oaicite:2]{index=2}
- ⏱️ Automated background tasks using APScheduler
- 🔐 Token-based request authentication
- 🔔 Webhook event forwarding (e.g. moderation logs)
- 🧹 Automated daily cleanup and pruning jobs

---

## Architecture

**Core Components:**

- `Core` – Loads application-wide configuration
- `Database` – Handles all persistent data operations
- `WebhookHandler` – Sends formatted event logs externally
- `Utilities` – Shared helper functions
- `Roblox` – Game-specific logic and data handling

---

## Background Jobs

The service runs scheduled jobs automatically:

| Job | Frequency | Description |
|----|---------|------------|
| Daily Procedure | Every 24 hours | Flushes database and logs role time data |
| Scheduler Check | Every 1 minute | Health check & tryout pruning |

---

## Authentication

Most endpoints require a JSON payload containing:

```json
{
  "AuthToken": "YOUR_SECRET_TOKEN"
}
