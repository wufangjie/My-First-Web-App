from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, Date, DateTime
from .base import Base, TINYINT


class User(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(20), nullable=False, comment="用户姓名", index=True)
    hashed_password = Column(String(60), nullable=False)
    email = Column(String(50), nullable=False, comment="邮箱", index=True)
    birth = Column(Date, comment="生日")
    sex = Column(TINYINT, comment="性别 {0: 男, 1: 女}", default=0)
    phone = Column(String(11), comment="手机")
    icon = Column(String(255), comment="头像url")
    add_time = Column(DateTime, comment="注册时间")
    state = Column(TINYINT, comment="是否注销 {0: 正常, 1: 注销}", default=0)

    # blogs = relationship("Blog", back_populates="user_id")
    # comments = relationship("Comment", back_populates="user_id")
    # thumbs = relationship("Thumb", back_populates="user_id")
