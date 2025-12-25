import uuid
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

# Tables
class UserAuth(SQLModel, table=True):
    user_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    
    info: Optional["UserInfo"] = Relationship(back_populates="auth")

class UserInfo(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="userauth.user_id")
    auth: Optional[UserAuth] = Relationship(back_populates="info")

class UserSignup(SQLModel):
    email: str
    password: str
    full_name: str
    age: int = None
    gender: str = None

