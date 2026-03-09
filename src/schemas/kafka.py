from datetime import datetime
from pydantic import BaseModel


class KafkaMessage(BaseModel):
    """Message format consumed from instagram / tiktok / youtube topics."""
    account_id: str
    requested_at: datetime
