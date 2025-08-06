from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional


class URLShortenRequest(BaseModel):
    url: HttpUrl
    shortcode: Optional[str] = None

    @field_validator("shortcode")
    @classmethod
    def validate_shortcode(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v


class URLShortenResponse(BaseModel):
    shortcode: str
    update_id: str


class URLUpdateRequest(BaseModel):
    url: HttpUrl


class URLUpdateResponse(BaseModel):
    shortcode: str
