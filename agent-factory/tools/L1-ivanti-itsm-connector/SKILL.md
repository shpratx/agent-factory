---
name: L1-ivanti-itsm-connector
description: Connector to create incidents in Ivanti ITSM from Aava (secure, validated, CI-friendly)
trigger: When the user asks to create or escalate incidents into Ivanti ITSM
---

# L1 Ivanti ITSM Connector

Purpose

This tool integrates Aava with Ivanti ITSM to create incidents programmatically. It validates input, enforces secure configuration, and returns a generic success/failure result suitable for use in automation and agent workflows.

Files

- `ivanti_connector.py` - Connector implementation
- `requirements.txt` - Python dependencies
- `tests/test_ivanti_connector.py` - Unit tests

Configuration

Provide the following environment variables securely (CI secrets or platform secret store):

- `IVANTI_ENDPOINT` - full HTTPS endpoint for the Ivanti connector
- `IVANTI_API_KEY` - API key for the integration

Security

- Input fields are validated with `pydantic`.
- Secrets must be provided via environment variables or a secure secret manager.
- TLS certificate verification is enforced by default.

Usage

Use this tool from within Aava/agent workflows to create incidents. The tool returns only high-level messages; callers should not assume detailed HTTP response content.
