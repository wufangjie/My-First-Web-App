import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    birth: datetime.date
    sex: int = 0
    phone: str = ""
    icon: str = ""


class UserUpdate(BaseModel):
    """
    TODO: email, username, password 暂定不能改, 以后会用 email 发送 token 来处理
    """
    # username: Optional[str]
    # email: Optional[str]
    # password: Optional[str]
    birth: Optional[datetime.date]
    sex: Optional[int]
    phone: Optional[str]
    icon: Optional[str]


# class UserCancel(BaseModel):
#     # 注销, 已经有 current_user, 就不需要其他数据了
#     pass


class UserResp(BaseModel):
    id: int #Optional[int] = None
    username: str
    sex: int = Field(..., description="{0: 男, 1: 女}", le=1, ge=0)
    icon: str

    class Config:
        orm_mode = True
