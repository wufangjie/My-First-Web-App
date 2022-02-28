from datetime import datetime
from pydantic import BaseModel


class CommentCreate(BaseModel):
    blog_id: int
    content: str
    re: int = 0


class CommentUpdate(BaseModel):
    """
    who: blog_id's owner or comment's owner
    which: only state
    """
    id: int
    state: int


class CommentRemove(BaseModel):
    id: int


class CommentResp(BaseModel):
    id: int
    blog_id: int
    user_id: int
    content: str
    add_time: datetime
    re: int
    # 不需要 state, 而是作为筛选条件

    class Config:
        orm_mode = True
