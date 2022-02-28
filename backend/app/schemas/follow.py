from datetime import datetime
from pydantic import BaseModel, Field
from .user import UserResp


class FollowBase(BaseModel):
    followed_id: int


class FollowCreate(FollowBase):
    focus: bool = Field(False, description="是否为特别关注")


class FollowUpdate(FollowBase):
    """Only to modify focus or not"""
    focus: bool = Field(False, description="是否为特别关注")


class FollowCancel(FollowBase):
    """Use updating state to implement cancel follow"""
    pass


class FollowResp(UserResp):
    mod_time: datetime
    focus: bool
