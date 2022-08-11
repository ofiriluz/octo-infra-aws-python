from pydantic import BaseModel, Field


class FindEC2InstanceCredentials(BaseModel):
    instance_id: str = Field(description="Instance ID to retrieve the ")
    private_key_path: str = Field(description="Private key path to use for decryption")
    # 4 Minutes is the documented max time for password retrieval
    retry_timeout_seconds: int = Field(description="Seconds to retry retrieving password if empty, "
                                                   "Might mean that the instance is not fully status check validated",
                                       default=240)
