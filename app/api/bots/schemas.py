from pydantic import BaseModel


class BotSchema(BaseModel):
    token: str
    type: str

