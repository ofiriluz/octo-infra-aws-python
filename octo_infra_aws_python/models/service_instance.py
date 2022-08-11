from pydantic import BaseModel, Field
from typing import Dict


class ServiceInstance(BaseModel):
    namespace: str = Field()
    service: str = Field()
    instance: str = Field()
    attributes: Dict[str, str] = Field()
