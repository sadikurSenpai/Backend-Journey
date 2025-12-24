from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class BlogPost(SQLModel, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    date : datetime = Field(default_factory=datetime.utcnow)
    title : str
    text : str