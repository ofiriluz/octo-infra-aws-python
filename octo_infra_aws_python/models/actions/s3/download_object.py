from pydantic import BaseModel, Field


class DownloadObject(BaseModel):
    bucket_name: str = Field(description="Bucket to download from")
    object_path: str = Field(description="Object path in s3 to download")
    output_path: str = Field(description="Output path of the object")
