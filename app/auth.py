"""接口认证依赖。"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import API_TOKEN


security = HTTPBearer(auto_error=False)
"""Bearer token 解析器。"""


async def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> None:
    """校验请求头中的 Bearer token。"""

    if credentials is None or credentials.scheme.lower() != "bearer" or credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
