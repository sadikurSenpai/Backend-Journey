from pydantic import BaseModel, Field

class TodoItem(BaseModel):
    title: str = Field(description="The task details", default='Run in the morning.')
    is_done: bool = False