from uuid import UUID
from pydantic import BaseModel


class KafkaMessage(BaseModel):
    user_id: UUID
    account_id: str
    access_token: str | None = None
    refresh_token: str | None = None
