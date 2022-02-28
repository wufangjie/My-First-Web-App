from datetime import datetime
from typing import List
from pydantic import BaseModel


class ThumbBase(BaseModel):
    blog_id: int


class ThumbCreate(ThumbBase):
    pass


class ThumbUpdate(ThumbBase):
    """Use updating state to implement cancel thumb"""
    pass


class ThumbCancel(ThumbBase):
    """Use updating state to implement cancel thumb"""
    pass
