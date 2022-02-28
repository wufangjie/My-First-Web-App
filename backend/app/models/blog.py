from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime
from .base import Base, TINYINT


class Blog(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    content = Column(String(140), comment="内容")
    add_time = Column(DateTime, comment="发布时间")
    state = Column(TINYINT, comment="状态: {-3: 永久删除, -2: 回收站, -1: 草稿, 0: 正常, 1: 仅自己可见}", default=0)

    # user_id = relationship("User", back_populates="blogs")
    # # comments = relationship("Comment", back_populates="blog_id")
    # # thumbs = relationship("Thumb", back_populates="blog_id")
    # pictures = relationship("Picture", back_populates="blog_id")
