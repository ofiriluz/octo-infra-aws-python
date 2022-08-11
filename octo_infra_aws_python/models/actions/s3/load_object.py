from pydantic import BaseModel, Field


class LoadObject(BaseModel):
    bucket_name: str = Field(description="Bucket to load from")
    object_path: str = Field(description="Object path in s3 to load")
