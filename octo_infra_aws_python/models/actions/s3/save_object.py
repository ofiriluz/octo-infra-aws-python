from pydantic import BaseModel, Field


class SaveObject(BaseModel):
    bucket_name: str = Field(description="Bucket to save to")
    object_path: str = Field(description="Object path in s3 to save to")
    body: bytes = Field(description="Data to save")
