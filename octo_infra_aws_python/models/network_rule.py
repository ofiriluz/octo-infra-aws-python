from pydantic import BaseModel, Field, conint
from typing import List


class NetworkRule(BaseModel):
    protocol: str = Field(default="tcp")  # AWS indicates -1 to be all protocols
    from_port: conint(ge=-1, le=65535) = Field()  # AWS indicates -1 to be all ports
    to_port: conint(ge=-1, le=65535) = Field()  # AWS indicates -1 to be all ports
    allowed_cidr: List[str] = Field(default=[])
    allowed_groups: List[str] = Field(default=[])
