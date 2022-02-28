from .token import Token, TokenPayload
from .message import Message
from .user import UserCreate, UserUpdate, UserResp
from .follow import FollowCreate, FollowUpdate, FollowCancel, FollowResp
from .thumb import ThumbCreate, ThumbUpdate, ThumbCancel

from .blog import BlogCreate, BlogUpdate, BlogRemove#, BlogRe
from .blog import BlogSimple, BlogsResp
from .picture import PictureCreate, PictureUpdate, PictureRemove
from .comment import CommentCreate, CommentUpdate, CommentRemove, CommentResp

# from typing import List
# from pydantic import BaseModel


# class BlogFull(BaseModel):
#     blog_id: int
#     content: str
#     user: UserInDB
#     pictures: List[str] # all <= 9
#     thumbs: List[ThumbInDB] # top 10
#     comments: List[CommentInDB]

    # 如果是类朋友圈的话, thumbs 和 comments 需要 follow 了才能查看?
    # 不过既然是 follow 这种弱关系, 这样做是没有必要的
