from datetime import datetime
from pydantic import BaseModel, Field


class SparkletCreate(BaseModel):
    to_name: str = Field(..., max_length=30)
    from_name: str = Field(..., max_length=30)
    message: str = Field(..., max_length=140)
    background_color: str = Field(default="#f0f0f0")
    card_color: str = Field(default="#ffffff")
    text_color: str = Field(default="#333333")


class Sparklet(BaseModel):
    id: int
    image_filename: str
    to_name: str
    from_name: str
    message: str
    date_created: datetime
    background_color: str
    card_color: str
    text_color: str
