"""Common result of one engine call, whatever the surface."""

from typing import Any, Literal

from pydantic import BaseModel, Field

Surface = Literal["chatgpt_api", "google_ai_mode", "chatgpt_app_manual", "gemini_app_manual"]


class Citation(BaseModel):
    url: str
    title: str | None = None


class Usage(BaseModel):
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0  # already included in output_tokens


class EngineResponse(BaseModel):
    surface: Surface
    provider: str
    model: str | None = None
    text: str
    citations: list[Citation] = Field(default_factory=list)
    searches: int = 0
    usage: Usage = Field(default_factory=Usage)
    cost_usd: float = 0.0
    empty: bool = False  # the surface answered without an AI answer (not an error)
    raw: dict[str, Any] = Field(default_factory=dict)
