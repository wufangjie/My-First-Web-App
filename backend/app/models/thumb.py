from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean
from .base import Base


class Thumb(Base):
    blog_id = Column(Integer, ForeignKey("blog.id"), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, comment="点赞用户", index=True)
    add_time = Column(DateTime, comment="点赞时间") # 需要更新
    state = Column(Integer, comment="状态 {正数表示点赞, 负数表示取消, 绝对值为次数}")

    # blog_id = relationship("Blog", back_populates="thumbs") # blog 被赞次数
    # user_id = relationship("User", back_populates="thumbs") # user 点赞次数
