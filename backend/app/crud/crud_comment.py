from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from collections import defaultdict

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, over

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.blog import Blog
from app.models.comment import Comments
from app.schemas.comment import CommentCreate, CommentUpdate
from app.schemas.blog import BlogSimple

LIMIT_N = 20


class CRUDComment(CRUDBase[Comments, CommentCreate, CommentUpdate]):
    def create_by_user_id(
            self, db: Session, *, obj_in: CommentCreate, user_id: int
    ) -> Comments:
        db_obj = Comments(
            user_id=user_id,
            add_time=datetime.utcnow(),
            **jsonable_encoder(obj_in))
        db.add(db_obj)
        db.commit()
        return db_obj

    def get_comments_by_blog_id(
            self,
            db: Session,
            *,
            blog_id: int,
            skip: int = 0,
            limit: Optional[int] = LIMIT_N
    ) -> List[Comments]:
        return (db
                .query(Comments)
                .filter(Comments.blog_id == blog_id)
                .filter(Comments.state == 0)
                .offset(skip)
                .limit(limit)
                .order_by(Comments.id)
                .all()
        )

    def get_comments_by_blog_ids(
            self,
            db: Session,
            *,
            blog_ids: List[int], # 一般不会太长, 所以用 in 性能也还可以
            limit: int = 10 # 多个 blog_id 的, 不可能取全部
    ) -> List[List[Comments]]: # actually f_rank
        f_rank = func.rank().over(
            partition_by=Comments.blog_id, order_by=Comments.id
        ).label("f_rank")
        subquery = (db
                    .query(Comments, f_rank)
                    .filter(Comments.blog_id.in_(blog_ids))
                    .filter(Comments.state == 0)
                    .subquery()
        )
        temp = (db
                .query(subquery)
                .filter(subquery.c.f_rank <= limit)
                .order_by(subquery.c.blog_id, subquery.c.f_rank)
                .all()
        )
        dct = defaultdict(list)
        for row in temp:
            dct[row.blog_id].append(row)
        return [dct.get(blog_id, []) for blog_id in blog_ids]

    def get_blogs_commented_by_user_id(
            self,
            db: Session,
            *,
            user_id: int,
            before: Optional[int] = None, # before blog_id
            skip: Optional[int] = None,
            limit: int = LIMIT_N
    ) -> List[BlogSimple]:
        filter_cond = before is None or Blog.id < before
        res = (db
               .query(
                   func.max(Comments.add_time).label("sp_time"),
                   *Blog.__table__.c
               )
               .join(Blog, Comments.blog_id == Blog.id)
               .filter(Comments.user_id == user_id)
               .filter(Comments.state == 0)
               .filter(Blog.state == 0)
               .filter(filter_cond)
               .group_by(Comments.blog_id)
               .order_by(desc(Comments.blog_id))#, Comments.id)
               .offset(skip)
               .limit(limit)
               .all()
        )
        return res


comment = CRUDComment(Comments)
