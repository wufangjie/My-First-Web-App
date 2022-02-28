from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
#from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.api import deps
from app.core.config import settings

router = APIRouter()


@router.post("/create", response_model=schemas.Message)
def comment_create(
        *,
        db: Session = Depends(deps.get_db),
        comment_in: schemas.CommentCreate,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    # can not comment non-public blog
    blog_db = crud.blog.get_by_id(db, id=comment_in.blog_id)
    if blog_db.state != 0:
        raise HTTPException(status_code=403, detail="Forbidden")

    crud.comment.create_by_user_id(
        db, obj_in=comment_in, user_id=current_user.id
    )
    return schemas.Message()


@router.post("/remove", response_model=schemas.Message)
def comment_remove(
        *,
        db: Session = Depends(deps.get_db),
        comment_in: schemas.CommentRemove,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    comment_db = crud.comment.get_by_id(db, comment_in.id)
    if comment_db is None:
        raise HTTPException(status_code=404, detail="No such comment")
    elif comment_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    crud.comment.update(db, db_obj=comment_db, obj_in={"state": 1})
    return schemas.Message()
