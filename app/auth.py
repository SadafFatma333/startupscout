# app/auth.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from psycopg import connect
from config.settings import DB_CONFIG
from utils.auth import hash_password, verify_password, create_jwt, verify_jwt

router = APIRouter(prefix="/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class MeOut(BaseModel):
    user_id: int
    email: EmailStr

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------
@router.post("/register")
def register(payload: RegisterIn):
    email = payload.email.lower().strip()
    pw_hash = hash_password(payload.password)

    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered.")
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, pw_hash),
            )
            uid = cur.fetchone()[0]

    token = create_jwt({"sub": uid, "email": email})
    return {"token": token}

@router.post("/login")
def login(payload: LoginIn):
    email = payload.email.lower().strip()

    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="Invalid credentials.")
            uid, pw_hash = row

    if not verify_password(payload.password, pw_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    token = create_jwt({"sub": uid, "email": email})
    return {"token": token}

def get_current_user(x_auth_token: str | None = Header(default=None)) -> MeOut:
    if not x_auth_token:
        raise HTTPException(status_code=401, detail="Missing token.")
    payload = verify_jwt(x_auth_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid/expired token.")
    try:
        uid = int(payload["sub"])
        email = payload.get("email")
        return MeOut(user_id=uid, email=email)  # type: ignore[arg-type]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

@router.get("/me", response_model=MeOut)
def me(user: MeOut = Depends(get_current_user)):
    return user
