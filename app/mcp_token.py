from datetime import datetime, timedelta, timezone

import jwt

from app.config.config import SECRET_KEY

MCP_ALGORITHM = 'HS256'
MCP_AUDIENCE = 'mcp'
MCP_TOKEN_EXPIRE_MINUTES = 5

def create_mcp_token(user_id:id)->str:
    now = datetime.now(timezone.utc)

    payload = {
        'sub': str(user_id),
        'aud': MCP_AUDIENCE,
        'iat': now,
        'exp': now + timedelta(minutes=MCP_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=MCP_ALGORITHM)