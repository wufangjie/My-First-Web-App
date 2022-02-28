from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogUpdate, BlogSimple


LIMIT_N = 20

class CRUDBlog(CRUDBase[Blog, BlogCreate, BlogUpdate]):

    def create_by_user(self, db: Session, *, obj_in: BlogCreate, user_id: int) -> Blog:
        db_obj = Blog(
            user_id=user_id,
            add_time=datetime.utcnow(),
            **jsonable_encoder(obj_in),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_blogs_by_user_id_with_state(
            self,
            db: Session,
            *,
            user_id: int,
            before: Optional[int] = None, # 防止下拉出现重复, 0 表示不限制
            skip: Optional[int] = None, # 和 before 并不冲突, 跳页时有用
            limit: int = LIMIT_N,
            state: int = 2,
            # { 0: 公开, -1: 草稿, -2: 回收站, 1: 仅自己, 2: 公开+仅自己 }
    ) -> List[BlogSimple]:
        filter_before = before is None or Blog.id < before
        if state == 2:
            filter_state = Blog.state >= 0
        else:
            filter_state = Blog.state == state
        return (db
                .query(Blog)
                .filter(Blog.user_id == user_id)
                .filter(filter_before)
                .filter(filter_state)
                .order_by(desc(Blog.id))
                .offset(skip)
                .limit(limit)
                .all()
        )

    def get_blogs_by_user_ids(
            self,
            db: Session,
            *,
            user_ids: List[int],
            before: Optional[int] = None,
            skip: Optional[int] = None,
            limit: int = LIMIT_N,
    ) -> List[BlogSimple]:
        filter_cond = before is None or Blog.id < before
        return (db
                .query(Blog)
                .filter(Blog.user_id.in_(user_ids))
                .filter(filter_cond)
                .filter(Blog.state == 0)
                .order_by(desc(Blog.id))
                .offset(skip)
                .limit(limit)
                .all()
        )

    def get_blogs_by_blog_ids(
            self,
            db: Session,
            *,
            blog_ids: List[int],
            before: Optional[int] = None,
            skip: Optional[int] = None,
            limit: int = LIMIT_N,
    ) -> List[BlogSimple]:
        """example: find all my recent comments as well as their blogs"""
        filter_cond = before is None or Blog.id < before
        return (db
                .query(Blog)
                .filter(Blog.id.in_(blog_ids))
                .filter(filter_cond)
                #.order_by(desc(Blog.id))
                .offset(skip)
                .limit(limit)
                .all()
        )


blog = CRUDBlog(Blog)
