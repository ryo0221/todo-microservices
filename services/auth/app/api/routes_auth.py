from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from ..db.session import get_db
from ..models.user import User
from ..core.security import hash_password, verify_password, create_access_token, verify_token
from ..core.dependencies import get_current_user


router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # 既存ユーザ確認
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    現在のユーザー情報を返す。
    """
    return {"user": current_user["sub"]}

@router.post("/refresh")
def refresh_token(request: RefreshRequest):
    """
    有効なリフレッシュトークンを検証し、新しいアクセストークンを発行する。
    """
    payload = verify_token(request.refresh_token, "refresh")
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired refresh token")

    new_access = create_access_token(payload["sub"])
    return {"access_token": new_access}