from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.follow import Follow
from app.models.user import User
from app.schemas.follow import FollowCreate, FollowUpdate, FollowResp

LIMIT_N = 20


class CRUDFollow(CRUDBase[Follow, FollowCreate, FollowUpdate]):
    def get_by_primary_keys(
            self, db: Session, *, followed_id: int, follower_id: int
    ) -> Optional[Follow]:
        return (db
                .query(Follow)
                .filter(Follow.followed_id == followed_id)
                .filter(Follow.follower_id == follower_id)
                .first()
        )

    def create_by_follower(
            self, db: Session, *, obj_in: FollowCreate, follower_id
    ) -> Follow:
        now = datetime.utcnow()
        db_obj = Follow(
            followed_id=obj_in.followed_id,
            follower_id=follower_id,
            add_time=now,
            mod_time=now,
            state=1,
            focus=obj_in.focus
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: Follow,
            obj_in: Union[FollowUpdate, Dict[str, Any]]
    ) -> Follow:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        update_data["mod_time"] = datetime.utcnow()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_followed_by_follower(
            self,
            db: Session,
            *,
            follower: int,
            skip: Optional[int] = None,
            limit: Optional[int] = LIMIT_N
    ) -> List[Follow]:
        # TODO: 当查询的人不是 current_user, 需不需要展示特别关注 (是否为隐私)
        return (db
                .query(Follow)
                .filter(Follow.follower_id == follower)
                .filter(Follow.state > 0)
                .order_by(desc(Follow.focus), desc(Follow.mod_time))
                .offset(skip)
                .limit(limit)
                .all()
        )

    def get_follower_by_followed(
            self,
            db: Session,
            *,
            followed: int,
            skip: Optional[int] = None,
            limit: Optional[int] = LIMIT_N
    ) -> List[Follow]:
        # TODO: 被关注者, 关不关心自己是否被特别关注?
        return (db
                .query(Follow)
                .filter(Follow.followed_id == followed)
                .filter(Follow.state > 0)
                .order_by(desc(Follow.focus), desc(Follow.mod_time))
                .offset(skip)
                .limit(limit)
                .all()
        )

    def get_followed_users_by_follower(
            self,
            db: Session,
            *,
            follower: int,
            skip: Optional[int] = None,
            limit: Optional[int] = LIMIT_N
    ) -> List[FollowResp]:
        # TODO: 当查询的人不是 current_user, 需不需要展示特别关注 (是否为隐私)
        return (db
                .query(
                    User.id,
                    User.username,
                    User.sex,
                    User.icon,
                    Follow.mod_time,
                    Follow.focus
                )
                .join(User, Follow.followed_id == User.id)
                .filter(Follow.follower_id == follower)
                .filter(Follow.state > 0)
                .order_by(desc(Follow.focus), desc(Follow.mod_time))
                .offset(skip)
                .limit(limit)
                .all()
        )

    def get_following_users_by_follower(
            self,
            db: Session,
            *,
            followed: int,
            skip: Optional[int] = None,
            limit: Optional[int] = LIMIT_N
    ) -> List[FollowResp]:
        # TODO: 当查询的人不是 current_user, 需不需要展示特别关注 (是否为隐私)
        return (db
                .query(
                    User.id, User.username, User.sex, User.icon,
                    Follow.mod_time, Follow.focus
                )
                .join(User, Follow.follower_id == User.id)
                .filter(Follow.followed_id == followed)
                .filter(Follow.state > 0)
                .order_by(desc(Follow.focus), desc(Follow.mod_time))
                .offset(skip)
                .limit(limit)
                .all()
        )


follow = CRUDFollow(Follow)
