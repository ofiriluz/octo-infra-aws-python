from pydantic import BaseModel, Field
from typing import List
from typing_extensions import Annotated


class NetworkRule(BaseModel):
    protocol: str = Field(default="tcp")  # AWS indicates -1 to be all protocols
    from_port: Annotated[int, Field(ge=-1, le=65535)]  # AWS indicates -1 to be all ports
    to_port: Annotated[int, Field(ge=-1, le=65535)]  # AWS indicates -1 to be all ports
    allowed_cidr: List[str] = Field(default_factory=list)
    allowed_groups: List[str] = Field(default_factory=list)
