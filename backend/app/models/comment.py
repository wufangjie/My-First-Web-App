from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime
from .base import Base, TINYINT


class Comments(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    blog_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, comment="评论用户", index=True)
    content = Column(String(140), nullable=False, comment="评论内容")
    add_time = Column(DateTime, nullable=False, comment="评论时间")
    re = Column(Integer, comment="回复谁, 0 表示 blog's owner", default=0)
    # ForeignKey("user.id"), # 因为有 0 存在, 所以不能设置 foreign key
    state = Column(TINYINT, comment="是否删除 {0: 正常, 1: 删除}", default=0)

    # blog_id = relationship("Blog", back_populates="comments")
    # user_id = relationship("User", back_populates="comments") # same name is ok?
    # # TODO: 本表之间的 relationship


# NOTE: 表名 comment 的话会和关键字冲突, 不能用:
# [SQL: INSERT INTO comment (blog_id
