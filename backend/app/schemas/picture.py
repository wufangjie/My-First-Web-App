import datetime
from pydantic import BaseModel
from typing import List, Optional


class PictureCreate(BaseModel):
    filename: str
    blog_id: int


class PictureUpdate(BaseModel):
    """dummy"""
    pass


class PictureRemove(BaseModel):
    """暂时不用, 详见 /models/picture.py"""
    id: int


# class PictureInDB(BaseModel):
#     """/pictures/{blog_id}_{id}.{ext}"""
#     id: int
#     blog_id: int
#     ext: str

#     class Config:
#         orm_mode = True
