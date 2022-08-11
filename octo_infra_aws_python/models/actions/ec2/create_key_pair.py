from typing import Dict, Optional

from pydantic import BaseModel, Field


class CreateKeypair(BaseModel):
    keypair_name: str = Field(description="Keypair name to create")
    private_key_file_path: Optional[str] = Field(
            description="If given, outputs the private key to the filesystem")
    # If delete is set, will delete the key
    use_if_exists: bool = Field(description="If keypair exists, use it",
                                default=False)
    delete_if_exists: bool = Field(description="If keypair exists, delete it",
                                   default=True)
    tags: Dict[str, str] = Field(description="Tags to be used for the keypair",
                                 default={})
