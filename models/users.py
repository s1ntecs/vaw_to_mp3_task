from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    username: Optional[str]
    token: Optional[str] = None

    class Settings:
        username = "user"

    class Config:
        schema_extra = {
            "example": {
                "username": "lexa"}
        }
