from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from .base import Base


class Follow(Base):
    followed_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)
    add_time = Column(DateTime, comment="开始关注时间") # 最早关注
    mod_time = Column(DateTime, comment="关注时间")     # 最近关注
    state = Column(Integer, comment="状态 {正数表示关注, 负数表示取消, 绝对值为次数}")
    focus = Column(Boolean, comment="是否为特别关注", default=False)
