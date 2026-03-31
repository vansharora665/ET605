These folders simulate three independent chapter teams integrating with the Merge System.

Each dummy module includes:
- `metadata.json`: the module-owned chapter metadata that would normally be exposed from `GET /api/chapter/metadata`
- `session_payload.json`: the session-end payload that would be sent to `POST /merge/interactions`

They are intentionally lightweight so the central backend stays the main implementation focus.
