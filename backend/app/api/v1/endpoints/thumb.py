from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app import models, schemas, crud


router = APIRouter()

@router.post("/make", response_model=schemas.Message)
def make_thumb(
        *,
        db: Session = Depends(deps.get_db),
        thumb_in: schemas.ThumbCreate,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    thumb_db = crud.thumb.get_by_primary_keys(
        db,
        blog_id=thumb_in.blog_id,
        user_id=current_user.id
    )
    if thumb_db is None:
        crud.thumb.create_by_user_id(
            db, obj_in=thumb_in, user_id=current_user.id
        )
    elif thumb_db.state < 0:
        crud.thumb.update(
            db,
            db_obj=thumb_db,
            obj_in={"add_time": datetime.utcnow(), "state": 1 - thumb_db.state}
        )
    else:
        return schemas.Message(state=-1, detail="Already thumbing")
    return schemas.Message()


@router.post("/cancel", response_model=schemas.Message)
def cancel_thumb(
        *,
        db: Session = Depends(deps.get_db),
        thumb_in: schemas.ThumbCancel,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    thumb_db = crud.thumb.get_by_primary_keys(
        db,
        blog_id=thumb_in.blog_id,
        user_id=current_user.id
    )
    if thumb_db is None:
        raise HTTPException(status_code=404, detail="No such thumbing existed")

    crud.thumb.update(
        db, db_obj=thumb_db, obj_in={"state": -abs(thumb_db.state)}
    )
    # 删除就不改时间了
    return schemas.Message()
