from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import UploadFile
from .user import UserResp
from .comment import CommentResp


class BlogCreate(BaseModel):
    content: str
    state: int = 0
    # 貌似不能把 file: UploadFile = File(...) 放到 pydantic model 里, 详见
    # https://github.com/tiangolo/fastapi/issues/657


class BlogUpdate(BaseModel):
    """Only can modify state"""
    id: int
    state: int


class BlogRemove(BaseModel):
    """Modify state to remove"""
    id: int
    state: int


class BlogRe(BaseModel): # 编辑后重新发布, 并删除源
    id: int
    content: str
    # TODO: 删除添加图片


# NOTE: BlogRe, BlogRemove 的时候
# 相关的图片, 评论, 点赞状态 暂时不变, 不过这些取出来都是要依赖 blog 的,
# 所以需要在那个时候判断

# NOTE: BlogRe (本身是小概率事件) 需要删除重新插入, 从而保持 id 按时间有序
# 而且这样能达到去掉原先的评论的效果 (本身就该如此)
# 但是也会导致图片的重复 (TODO: 先不管, 毕竟小概率事件)

# NOTE: 带全部信息的 Blog 定义在 __init__.py 中
# 因为要用到 UserInDB, PictureInDB, ThumbInDB, CommentInDB


class BlogSimple(BaseModel):
    id: int # TODO: 是否需要加 Optional
    user_id: int
    content: str
    add_time: datetime
    state: int

    sp_time: Optional[datetime] = Field(None, description="这个字段的作用是记录一些额外的信息, 比如特定用户的点赞或最后评论时间, 用于对该用户最近的活动做排序")


class BlogWithoutUserDetail(BlogSimple):
    pictures: List[str]
    comments: List[CommentResp]
    thumbs: List[int]
    c_total: int # 评论总数
    t_total: int # 点赞总数


class BlogsResp(BaseModel):
    blogs: List[BlogWithoutUserDetail]
    users: List[UserResp]
