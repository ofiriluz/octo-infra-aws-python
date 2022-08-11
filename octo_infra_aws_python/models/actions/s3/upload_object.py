from pydantic import BaseModel, Field


class UploadObject(BaseModel):
    bucket_name: str = Field(description="Bucket to upload to")
    input_path: str = Field(description="Input path to upload")
    object_path: str = Field(description="Object path in s3 to upload to")
