from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    state: int = 0 # 0 表示正常
    detail: str = "Done"
