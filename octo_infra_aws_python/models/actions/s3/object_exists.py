from pydantic import BaseModel, Field


class ObjectExists(BaseModel):
    bucket_name: str = Field(description="Bucket to check on")
    object_path: str = Field(description="Object path in s3 to download")
