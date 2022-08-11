from pydantic import BaseModel, Field
from typing import Dict, Optional


class FindServiceInstance(BaseModel):
    namespace: str = Field()
    service: str = Field()
    attributes_filter: Dict[str, str] = Field(default={})
    region: Optional[str] = Field()
