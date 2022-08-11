from pydantic import BaseModel, Field
from typing import Dict, Optional


class FindAsset(BaseModel):
    vpc_id: Optional[str] = Field()
    tags: Optional[Dict[str, str]] = Field()
    state: Optional[str] = Field()
