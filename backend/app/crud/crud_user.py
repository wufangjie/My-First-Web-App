from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils import re_simple_email


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_active_user(self, db: Session) -> List[User]:
        return db.query(User).filter(User.state == 0).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        obj_json = jsonable_encoder(obj_in)
        obj_json.pop('password')
        db_obj = User(
            hashed_password=get_password_hash(obj_in.password),
            add_time=datetime.utcnow(),
            # state=0, # which is default
            **obj_json,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, db_obj: User) -> Optional[User]:
        return self.update(db, db_obj=db_obj, obj_in={"state": 1})

    def update(
            self,
            db: Session,
            *,
            db_obj: User,
            obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
            self, db: Session, *, username: str, password: str
    ) -> Optional[User]:
        if re_simple_email.match(username):
            user = self.get_by_email(db, email=username)
        else:
            user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_users_by_user_ids(
            self, db: Session, *, user_ids: List[int]
    ) -> List[User]:
        return (db
                .query(User.id, User.username, User.sex, User.icon)
                .filter(User.id.in_(user_ids))
                .all()
        )


user = CRUDUser(User)
