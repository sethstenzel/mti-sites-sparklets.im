"""Shapes of the API payloads (documentation; the routes in main.py validate form fields)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Visibility = Literal["public", "restricted"]


class SparkletCreate(BaseModel):
    to_name: str = Field(..., max_length=20)
    from_name: str = Field(..., max_length=20)
    message: str = Field(..., max_length=140)
    background_color: str = Field(default="#f0f0f0", pattern=r"^#[0-9a-fA-F]{6}$")
    card_color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    text_color: str = Field(default="#333333", pattern=r"^#[0-9a-fA-F]{6}$")
    card_rotation: int = Field(default=5, ge=-10, le=10)
    entry_animation: str = "drop"
    font: str = "kalam"


class Sparklet(BaseModel):
    public_id: str  # random 22-char token; the only identifier clients ever see
    image_filename: str
    to_name: str
    from_name: str
    message: str
    background_color: str
    card_color: str
    text_color: str
    card_rotation: int
    entry_animation: str
    font: str
    visibility: Visibility
    created_at: datetime
    updated_at: datetime
