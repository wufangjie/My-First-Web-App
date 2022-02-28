import os
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.api import deps
from app.core.config import settings
from app.core import security

router = APIRouter()

re_bid_pid_ext = re.compile(r"^(\d+)_(\d+)\.([a-z]+)$")


@router.get("/pictures/{bid_pid_ext}", response_class=FileResponse)
def get_picture(
        *,
        db: Session = Depends(deps.get_db),
        bid_pid_ext: str,
        current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    found = re_bid_pid_ext.findall(bid_pid_ext)
    if not found:
        raise HTTPException(status_code=404, detail="Not Found")
    bid, pid, ext = found[0]

    blog = crud.blog.get_by_id(db, bid)
    if blog is None:
        raise HTTPException(status_code=404, detail="Not Found")
    if blog.user_id == current_user.id:
        if blog.state == -3:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        if blog.state != 0:
            raise HTTPException(status_code=403, detail="Forbidden")

    picture = crud.picture.get_by_id(db, pid)
    if picture.state != 0:
        raise HTTPException(status_code=404, detail="Not Found")
    # 如果不这么做的话, 用户的私密图片也能被浏览
    # TODO: 如果我在 doc 里授权, 不 try it out, 直接访问是获取不到文件的
    # 但 try it out 又可以, 不太确定为什么 (可能是浏览器缓存?)
    return os.path.join(settings.PICTURE_ROOT, bid_pid_ext)
    # return Response(img, mimetype="image/png") # flask solution


# @router.post("pictures/remove", response_model=schemas.Message)
# def remove_picture(
#         )
