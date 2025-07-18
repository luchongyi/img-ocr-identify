from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import bcrypt
from sqlalchemy import select
from app.core.security import create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str

class RegisterResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

class LoginRequest(BaseModel):
    username: str
    password: str
    hours: int = 2  # 有效期小时数，默认2小时

class LoginResponse(BaseModel):
    secret_key: str
    expires_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

# @router.post("/register", response_model=RegisterResponse)
# async def register(
#     request: RegisterRequest,
#     db: AsyncSession = Depends(get_db)
# ):
#     # 检查用户名是否已存在
#     result = await db.execute(
#         select(User).where(User.username == request.username)
#     )
#     if result.scalar_one_or_none():
#         raise HTTPException(status_code=400, detail="用户名已存在")
#     # 密码加密
#     password_hash = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()
#     user = User(username=request.username, password_hash=password_hash)
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return RegisterResponse(id=user.id, username=user.username, created_at=user.created_at)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # 查找用户
    result = await db.execute(
        select(User).where(User.username == request.username, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    # 校验密码
    if not bcrypt.checkpw(request.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    # 生成 JWT token
    token, expire = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(hours=request.hours)
    )
    return TokenResponse(access_token=token, expires_at=expire) 
    