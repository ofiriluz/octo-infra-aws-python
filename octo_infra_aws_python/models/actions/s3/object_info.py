from pydantic import BaseModel, Field


class ObjectInfo(BaseModel):
    bucket_name: str = Field(description="Bucket of the object")
    object_path: str = Field(description="Object path in s3")
    object_size: int = Field(description="Size of the object")
    is_folder: bool = Field(description="Is the object a folder")
