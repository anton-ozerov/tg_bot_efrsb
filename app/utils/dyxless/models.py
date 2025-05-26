from pydantic import BaseModel


class ObjectDyxless(BaseModel):
    count: int | None
    data: list | None
    status: bool | None