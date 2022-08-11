from pydantic import BaseModel, Field
from typing import List


class FindObjects(BaseModel):
    bucket_name: str = Field(description="Bucket to find objects on")
    base_search_path: str = Field(description="Base search path to search objects on",
                                  default="")
    only_prefixes: bool = Field(description="Only folder prefixes",
                                default=False)
    filters: List[str] = Field(description="Wildcard filters for objects",
                               default_factory=list)
