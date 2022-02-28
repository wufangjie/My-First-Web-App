from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.api import deps
from app.core.config import settings
from app.core import security

router = APIRouter()


@router.post("/register", response_model=schemas.UserResp)
def register(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        # current_user: models.User = Depends(deps.get_current_user),
        # #不加这句就是不需要 oauth2 验证, docs 页面 api 右上角会带锁
) -> Any:
    user_db = crud.user.get_by_email(db, email=user_in.email)
    if user_db:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    same_name = crud.user.get_by_username(db, username=user_in.username)
    if same_name:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return crud.user.create(db, obj_in=user_in)


@router.post("/close_account", response_model=schemas.UserResp)
def close_account(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    user_db = crud.user.get_by_id(db, current_user.id)
    return crud.user.remove(db, db_obj=user_db)


@router.post("/update_info", response_model=schemas.UserResp)
def update_info(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    user_db = crud.user.get_by_id(db, current_user.id)
    return crud.user.update(db, db_obj=user_db, obj_in=user_in)
