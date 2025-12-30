import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from pydantic import BaseModel, EmailStr, Field as PydanticField

class UserAuth(SQLModel, table=True):
    user_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed: str

    info: Optional['UserInfo'] = Relationship(back_populates='auth')

class UserInfo(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None

    # Foreign key should reference the UserAuth table column name.
    # Do not generate a new UUID here — this field links to an existing `UserAuth.user_id`.
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="userauth.user_id")
    auth: Optional[UserAuth] = Relationship(back_populates="info")

class UserSignup(SQLModel):
    email: EmailStr
    password: str = PydanticField(..., min_length=6)
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
