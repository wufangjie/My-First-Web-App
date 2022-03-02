from typing import Any, Dict, List, Tuple, Optional, Union
from datetime import datetime
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, desc#, and_

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.blog import Blog
from app.models.thumb import Thumb
from app.schemas.thumb import ThumbCreate, ThumbUpdate
from app.schemas import BlogSimple


class CRUDThumb(CRUDBase[Thumb, ThumbCreate, ThumbUpdate]):
    def get_by_primary_keys(
            self, db: Session, *, blog_id: int, user_id: int
    ) -> Optional[Thumb]:
        return (db
                .query(Thumb)
                .filter(Thumb.blog_id == blog_id)
                .filter(Thumb.user_id == user_id)
                .first()
        )

    def create_by_user_id(
            self, db: Session, *, obj_in: ThumbCreate, user_id
    ) -> Thumb:
        db_obj = Thumb(
            blog_id=obj_in.blog_id,
            user_id=user_id,
            add_time=datetime.utcnow(),
            state=1,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_thumb_count_by_blog_id(
            self,
            db: Session,
            *,
            blog_id: int,
    ) -> int:
        return (db
                .query(Thumb)
                .filter(Thumb.blog_id == blog_id)
                .filter(Thumb.state > 0)
                .count()
        )

    def get_thumb_counts_by_blog_ids(
            self,
            db: Session,
            *,
            blog_ids: List[int],
    ) -> List[int]: # [count], len = len(blog_ids)
        dct = dict(db
                    .query(Thumb.blog_id, func.count("*").label("count"))
                    .filter(Thumb.blog_id.in_(blog_ids))
                    .filter(Thumb.state > 0)
                    .group_by(Thumb.blog_id)
                    .all()
        )
        return [dct.get(blog_id, 0) for blog_id in blog_ids]

    def get_thumb_user_ids_by_blog_id(
            self,
            db: Session,
            *,
            blog_id: int,
            skip: Optional[int] = None,
            limit: Optional[int] = None
    ) -> List[int]:
        return (db
                .query(Thumb.user_id)
                .filter(Thumb.blog_id == blog_id)
                .filter(Thumb.state > 0)
                .order_by(Thumb.add_time)
                .offset(skip)
                .limit(limit)
                .all()
        )

    def get_thumb_user_ids_by_blog_ids(
            self,
            db: Session,
            *,
            blog_ids: List[int],
            limit: int = 5 # 多个 blog 的时候, 只需要前五点赞
    ) -> List[List[int]]:
        f_rank = func.rank().over(
            partition_by=Thumb.blog_id, order_by=Thumb.add_time
        ).label("f_rank")
        subquery = (db
                    .query(Thumb.blog_id, Thumb.user_id, f_rank)
                    .filter(Thumb.blog_id.in_(blog_ids))
                    .filter(Thumb.state > 0)
                    .subquery()
        )
        temp = (db
                .query(subquery.c.blog_id, subquery.c.user_id)
                .filter(subquery.c.f_rank <= limit)
                .order_by(subquery.c.blog_id, subquery.c.f_rank)
                .all()
        )
        dct = defaultdict(list)
        for blog_id, user_id in temp:
            dct[blog_id].append(user_id)
        return [dct.get(blog_id, []) for blog_id in blog_ids]

    def get_blogs_thumbed_by_user_id(
            self,
            db: Session,
            *,
            user_id: int,
            before: Optional[datetime] = None,
            skip: Optional[int] = None,
            limit: int = 20,
    ) -> List[BlogSimple]:
        """我最近点赞的一些 blog id, 按点赞时间排序, 而不是 blog 发布顺序"""
        filter_cond = before is None or Thumb.add_time < before
        return (db
                .query(Thumb.add_time.label("sp_time"), *Blog.__table__.c)
                .join(Blog, Thumb.blog_id == Blog.id)
                .filter(Thumb.user_id == user_id)
                .filter(Thumb.state > 0)
                .filter(filter_cond)
                .filter(Blog.state == 0)
                .order_by(desc(Thumb.add_time))
                .offset(skip)
                .limit(limit)
                .all()
        )

thumb = CRUDThumb(Thumb)
