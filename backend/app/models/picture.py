from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime
from .base import Base, TINYINT


class Picture(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    blog_id = Column(Integer, ForeignKey("blog.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    ext = Column(String(4), nullable=False, comment="文件后缀")
    state = Column(TINYINT, nullable=False, comment="是否删除 {0: 正常, 1: 删除}", default=0)

    # NOTE:
    # state 先保留, 暂时不用, 像微信朋友圈也不能单独删除某一张图片
    # filename 貌似也没什么用, 暂时保留
    # user_id 和 add_time 都先不加


    # blog_id = relationship("Blog", back_populates="pictures")
