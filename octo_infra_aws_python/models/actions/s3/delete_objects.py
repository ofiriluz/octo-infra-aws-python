from pydantic import BaseModel, Field
from typing import List


class DeleteObjects(BaseModel):
    bucket_name: str = Field(description="Bucket to delete from")
    objects_path: List[str] = Field(description="Objects path in s3 to delete")
