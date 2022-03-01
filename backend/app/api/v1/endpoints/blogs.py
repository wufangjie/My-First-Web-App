import os
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import BackgroundTasks

from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.api import deps
from app.core.config import settings
from app.core import security

import shutil

router = APIRouter()

# NOTE: You can declare multiple File and Form parameters in a path operation,
# but you can't also declare Body fields that you expect to receive as JSON
# https://fastapi.tiangolo.com/tutorial/request-forms-and-files/?h=file+form

# @router.post("/uploadfile/")
# async def create_upload_file(file: Optional[UploadFile] = None):
#     if not file:
#         return {"message": "No upload file sent"}
#     else:
#         return {"filename": file.filename}


@router.post("/create", response_model=schemas.Message)#BlogInDB)
async def blog_create(
        *,
        db: Session = Depends(deps.get_db),
        pictures: List[UploadFile] = Form([], description="没有图片就不要加该字段, 千万不要发送空值"),
        #blog_in: schemas.BlogCreate = Body(..., embed=True),
        content: str = Form(...),
        state: int = Form(0, description="状态: {-3: 永久删除, -2: 回收站, -1: 草稿, 0: 正常, 1: 仅自己可见}", le=1, ge=-3),
        current_user: models.User = Depends(deps.get_current_user),
        background_tasks: BackgroundTasks,
) -> Any:
    # TODO: make it async
    blog_in = schemas.BlogCreate(content=content, state=state)
    blog_db = crud.blog.create_by_user(
        db, obj_in=blog_in, user_id=current_user.id
    )

    pics_in_db = []
    pics_valid = []
    for pic in pictures:
        name_without_ext, ext = pic.filename.rsplit('.')
        if ext in {"jpg", "png", "bmp", "jpeg"}:
            pics_in_db.append(
                models.Picture(
                    blog_id=blog_db.id,
                    filename=name_without_ext[-255:],
                    ext=ext,
                    state=0,
                )
            )
            pics_valid.append(pic)
    pics_in_db = crud.picture.insert_multi(db, pics=pics_in_db)
    background_tasks.add_task(save_pictures, pics_in_db, pics_valid)
    return schemas.Message()


def save_pictures(pics_in_db: List[models.Picture], pictures: List[UploadFile]):
    for pic_db, pic in zip(pics_in_db, pictures):
        with open(os.path.join(
                settings.PICTURE_ROOT,
                '{0.blog_id}_{0.id}.{0.ext}'.format(pic_db)
        ), "wb") as buffer:
            shutil.copyfileobj(pic.file, buffer)


@router.post("/remove", response_model=schemas.Message)
def blog_remove(
        *,
        db: Session = Depends(deps.get_db),
        blog_in: schemas.BlogRemove,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    blog_db = crud.blog.get_by_id(db, blog_in.id)
    if blog_db is None:
        raise HTTPException(status_code=404, detail="No such blog")
    elif blog_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    crud.blog.update(
        db,
        db_obj=blog_db,
        obj_in={"state": blog_in.state}
    )
    return schemas.Message()


@router.post("/update", response_model=schemas.Message)
def blog_update(
        *,
        db: Session = Depends(deps.get_db),
        blog_in: schemas.BlogUpdate,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    blog_db = crud.blog.get_by_id(db, blog_in.id)
    if blog_db is None:
        raise HTTPException(status_code=404, detail="No such blog")
    elif blog_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    crud.blog.update(
        db,
        db_obj=blog_db,
        obj_in={"state": blog_in.state}
    )
    return schemas.Message()
