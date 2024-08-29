from pydantic import BaseModel, Field
from typing import Dict, Optional


class FindAsset(BaseModel):
    vpc_id: Optional[str] = Field(default=None)
    tags: Optional[Dict[str, str]] = Field(default=None)
    state: Optional[str] = Field(default=None)
