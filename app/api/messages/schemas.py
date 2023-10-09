from pydantic import BaseModel, Field


class ButtonSchema(BaseModel):
    id: int
    name: str
    text: str
    keyboard_id: int


class UpdateButton(BaseModel):
    text: str = Field(..., max_length=50)


class MessageSchema(BaseModel):
    id: int
    text: str
    priority: int
    message_group_id: int
    keyboard_id: int | None
    callback_buttons: list[ButtonSchema] = []


class AddMessageSchema(BaseModel):
    text: str
    priority: int = Field(..., ge=1)



class UpdateMessageText(BaseModel):
    text: str


class Order(BaseModel):
    message_id: int = Field(..., ge=1)
    priority: int = Field(..., ge=1)


class UpdateOrder(BaseModel):
    order: list[Order]
