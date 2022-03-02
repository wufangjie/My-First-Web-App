from typing import Any, Optional, List, Union
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.api import deps
from app.core.config import settings
from app.core import security


router = APIRouter()


class Position(str, Enum):
    home = "home"
    self_only = "self-only"
    public = "public"
    draft = "draft"
    trash = "trash"

    @property
    def db_value(self):
        # TODO: use match if python >= 3.10
        if self == "home":
            return 2
        elif self == "self-only":
            return 1
        elif self == "public":
            return 0
        elif self == "draft":
            return -1
        elif self == "trash":
            return -2
        else:
            raise Exception("Unknown")


def get_blog_full_and_user_ids(
        db: Session,
        blog_lst: List[schemas.BlogSimple]
        #blog_lst: [List[models.Blog], List[schemas.BlogSingleTable_TT]]
) -> Any:
    blog_ids = [blog.id for blog in blog_lst]
    pictures = crud.picture.get_picture_urls_by_blog_ids(db, blog_ids=blog_ids)
    comments = crud.comment.get_comments_by_blog_ids(db, blog_ids=blog_ids)
    thumbs = crud.thumb.get_thumb_user_ids_by_blog_ids(db, blog_ids=blog_ids)
    c_count = crud.comment.get_comment_counts_by_blog_ids(db, blog_ids=blog_ids)
    t_count = crud.thumb.get_thumb_counts_by_blog_ids(db, blog_ids=blog_ids)

    ret_json = jsonable_encoder(blog_lst)
    user_ids = {blog.user_id for blog in blog_lst} # user_id ever been here
    for i, blog_id in enumerate(blog_lst):
        ret_json[i]["pictures"] = jsonable_encoder(pictures[i])
        ret_json[i]["comments"] = jsonable_encoder(comments[i])
        ret_json[i]["thumbs"] = jsonable_encoder(thumbs[i])
        ret_json[i]["c_total"] = c_count[i]
        ret_json[i]["t_total"] = t_count[i]

        for comment in comments[i]:
            user_ids.add(comment.user_id)
        user_ids.update(thumbs[i])
    return ret_json, user_ids



@router.get("/{user_id:int}/social", response_model=schemas.BlogsResp)
def user_social(
        user_id: int,
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
        before: Optional[int] = Query(
            None, description="下拉时使用, 默认值 None 表示不限制"
        ),
        skip: Optional[int] = Query(None, description="翻页时使用"),
        limit: int = Query(20, description="一次取数据条数", le=50, ge=10),
) -> Any:
    """自己和自己关注的人的最近几个 blogs (不同颜色标识, 自己和特别关注)"""
    if user_id != current_user.id:
        return HTTPException(status_code=403, detail="Forbidden")

    followed_lst = crud.follow.get_followed_by_follower(db, follower=user_id)
    user_ids = [user_id] + [followed.followed_id for followed in followed_lst]
    blog_lst = crud.blog.get_blogs_by_user_ids(
        db,
        user_ids=user_ids,
        before=before,
        skip=skip,
        limit=limit,
    )

    blog_full, user_ids = get_blog_full_and_user_ids(db, blog_lst)
    user_set = crud.user.get_users_by_user_ids(db, user_ids=list(user_ids))
    return {"blogs": blog_full, "users": user_set}


# NOTE: 装饰器中的 response_model 会显示在 docs 的 Schema 中
@router.get("/{user_id}/following", response_model=List[schemas.FollowResp])
def user_following(
        user_id: int,
        *,
        db: Session = Depends(deps.get_db),
        #current_user: models.User = Depends(deps.get_current_user),
        skip: int = Query(0, description="翻页时使用"),
        limit: int = Query(20, description="一次取数据条数", le=50, ge=10),
) -> Any:
    "用户在关注的人"
    # 因为不是常用功能, 不需要用 before
    return crud.follow.get_followed_users_by_follower(
        db, follower=user_id, skip=skip, limit=limit
    )


@router.get("/{user_id}/followed", response_model=List[schemas.FollowResp])
def user_followed(
        user_id: int,
        *,
        db: Session = Depends(deps.get_db),
        skip: int = Query(0, description="翻页时使用"),
        limit: int = Query(20, description="一次取数据条数", le=50, ge=10),
) -> Any:
    "关注该用户的人"
    return crud.follow.get_following_users_by_follower(
        db, followed=user_id, skip=skip, limit=limit
    )


@router.get("/{user_id}/thumbing", response_model=schemas.BlogsResp)
def user_thumbing(
        user_id: int,
        *,
        db: Session = Depends(deps.get_db),
        before: Optional[datetime] = Query(
            None,
            description="下拉时使用, 取该时间之前的数据, 默认 None 表不限制"
        ),
        skip: Optional[int] = Query(None, description="翻页时使用"),
        limit: int = Query(20, description="一次取数据条数", le=50, ge=10),
) -> Any:
    "用户最近点赞的 blog"
    # NOTE: 需要考虑 blog 被删除和被设为仅自己可见的情况
    blog_lst = crud.thumb.get_blogs_thumbed_by_user_id(
        db, user_id=user_id, before=before, skip=skip, limit=limit
    )
    blog_full, user_ids = get_blog_full_and_user_ids(db, blog_lst)
    user_set = crud.user.get_users_by_user_ids(db, user_ids=list(user_ids))
    return {"blogs": blog_full, "users": user_set}


@router.get("/{user_id}/comments")#, response_model=schemas.UserInDB)
def user_comments(
        user_id: int,
        *,
        db: Session = Depends(deps.get_db),
        before: Optional[datetime] = Query(
            None,
            description="下拉时使用, 取该时间之前的数据, 默认 None 表不限制"
        ),
        skip: Optional[int] = Query(None, description="翻页时使用"),
        limit: int = Query(20, description="一次取数据条数", le=50, ge=10),
) -> Any:
    """
    用户最近的评论过的 blog

    如果按评论时间排序, 因为可能评论多次, 下滑时可能会重复, 这样就只能在前端处理
    按 blog 排序可能更好
    """
    blog_lst = crud.comment.get_blogs_commented_by_user_id(
        db, user_id=user_id, before=before, skip=skip, limit=limit
    )
    blog_full, user_ids = get_blog_full_and_user_ids(db, blog_lst)
    user_set = crud.user.get_users_by_user_ids(db, user_ids=list(user_ids))
    return {"blogs": blog_full, "users": user_set}



# NOTE: 这个函数必须放在最后, 否则会使其它的 /{user_id:int}/* 失效
# {pos:Position} 也会报错
@router.get("/{user_id:int}/{pos}", response_model=schemas.BlogsResp)
def user_recent_blog(
        user_id: int,
        pos: Position,
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
        before: Optional[int] = Query(
            None, description="下拉时使用, 默认值 None 表示不限制"
        ),
        skip: Optional[int] = Query(None, description="翻页时使用"),
        limit: int = Query(20, description="一次取数据条数", le=50, ge=10),
) -> Any:
    """用户最近的一些 blogs"""
    if user_id != current_user.id and pos != Position.public:
        return RedirectResponse(f"/{user_id}/public")

    blog_lst = crud.blog.get_blogs_by_user_id_with_state(
        db,
        user_id=user_id,
        before=before,
        skip=skip,
        limit=limit,
        state=pos.db_value
    )

    # TODO: 排序支持, 比如被点赞最多的 blog? 太复杂, 之后再说
    # 因为会多次用到相同的 user, 所以我把所有用到的 user 单独拿出来?
    # 不知道这样是不是正确做法
    # 用户需要的字段是: id(链接), 用户名, 头像(?)

    blog_full, user_ids = get_blog_full_and_user_ids(db, blog_lst)
    user_set = crud.user.get_users_by_user_ids(db, user_ids=list(user_ids))
    return {"blogs": blog_full, "users": user_set}
