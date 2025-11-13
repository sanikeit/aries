# Backend Configuration and Environment Variables

The backend loads configuration from `.env` via `pydantic-settings` (`app/core/config.py`).

## Environment Variables
- `DATABASE_URL` (default: `sqlite+aiosqlite:///./aries.db`)
- `JWT_SECRET_KEY` (default: development key; change in production)
- `JWT_ALGORITHM` (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `30`)
- `PULSAR_URL` (default: `pulsar://localhost:6650`) — optional
- `KAFKA_BOOTSTRAP_SERVERS` (default: `localhost:9092`) — optional
- `HLS_OUTPUT_DIR` (default: `./hls_streams`)
- `MODEL_CONFIG_DIR` (default: `./configs`)
- `MODEL_WEIGHTS_DIR` (default: `./models`)
- `API_KEY_HEADER_NAME` (default: `X-API-Key`)
- `CORS_ORIGINS` (default: `[http://localhost:3000, http://localhost:5173]`)
- `RATE_LIMIT_PER_MINUTE` (default: `100`)

## Example .env
```
DATABASE_URL=sqlite+aiosqlite:///./aries.db
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
HLS_OUTPUT_DIR=./hls_streams
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## Notes
- Never commit real secrets to version control.
- For production, use a managed secrets solution and rotate keys regularly.
- Keep `HLS_OUTPUT_DIR` on a fast disk; ensure appropriate permissions.
