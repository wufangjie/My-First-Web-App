from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app import models, schemas, crud


router = APIRouter()

@router.post("/make", response_model=schemas.Message)
def make_follow(
        *,
        db: Session = Depends(deps.get_db),
        follow_in: schemas.FollowCreate,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    follow_db = crud.follow.get_by_primary_keys(
        db,
        followed_id=follow_in.followed_id,
        follower_id=current_user.id
    )
    if follow_db is None:
        if follow_in.followed_id == current_user.id:
            raise HTTPException(status_code=403, detail="Can not follow oneself")
        else:
            crud.follow.create_by_follower(
                db, obj_in=follow_in, follower_id=current_user.id
            )
    elif follow_db.state < 0:
        crud.follow.update(
            db,
            db_obj=follow_db,
            obj_in={
                "mod_time": datetime.utcnow(),
                "state": 1 - follow_db.state,
                "focus": follow_in.focus
            }
        )
    else:
        return schemas.Message(state=-1, detail="Already following")
    return schemas.Message()


@router.post("/cancel", response_model=schemas.Message)
def cancel_follow(
        *,
        db: Session = Depends(deps.get_db),
        follow_in: schemas.FollowCancel,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    follow_db = crud.follow.get_by_primary_keys(
        db,
        followed_id=follow_in.followed_id,
        follower_id=current_user.id
    )
    if follow_db is None:
        raise HTTPException(status_code=404, detail="No such following")
    elif follow_db.state > 0:
        crud.follow.update(
            db,
            db_obj=follow_db,
            obj_in={
                "mod_time": datetime.utcnow(),
                "state": -follow_db.state,
                "focus": False
            }
        )
    else:
        return schemas.Message(state=-1, detail="Already canceled")
    return schemas.Message()


@router.post("/focus", response_model=schemas.Message)
def focus_follow(
        *,
        db: Session = Depends(deps.get_db),
        follow_in: schemas.FollowUpdate,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    follow_db = crud.follow.get_by_primary_keys(
        db,
        followed_id=follow_in.followed_id,
        follower_id=current_user.id
    )
    if follow_db is None:
        raise HTTPException(status_code=404, detail="No such following")
    elif follow_db.focus != follow_in.focus:
        crud.follow.update(
            db,
            db_obj=follow_db,
            obj_in={"mod_time": datetime.utcnow(), "focus": follow_in.focus}
        )
    else:
        return schemas.Message(state=-1, detail="Nothing to update")
    return schemas.Message()
