from typing import Any, Dict, List, Optional, Union
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.picture import Picture
from app.schemas.picture import PictureCreate, PictureUpdate


class CRUDPicture(CRUDBase[Picture, PictureCreate, PictureUpdate]):
    def insert_multi(self, db: Session, *, pics: List[Picture]) -> List[Picture]:
        db.add_all(pics)
        db.flush() # need?
        db.commit()
        return pics # will update automaticlly, need return?

    def get_picture_urls_by_blog_id(
            self, db: Session, *, blog_id: int
    ) -> List[str]:
        url = func.concat(Picture.blog_id, '_', Picture.id, '.', Picture.ext)
        return (db
                .query(url)
                .filter(Picture.blog_id == blog_id)
                .order_by(Picture.id)
                .all()
        )

    def get_picture_urls_by_blog_ids(
            self, db: Session, *, blog_ids: List[int]
    ) -> List[List[str]]:
        temp = (db
                .query(Picture.blog_id, Picture.id, Picture.ext)
                .filter(Picture.blog_id.in_(blog_ids))
                .order_by(Picture.blog_id, Picture.id) # id 有序, 不过以防万一
                .all()
        )
        dct = defaultdict(list)
        for pic in temp:
            dct[pic.blog_id].append("{0.blog_id}_{0.id}.{0.ext}".format(pic))
        return [dct.get(blog_id, []) for blog_id in blog_ids]


picture = CRUDPicture(Picture)
