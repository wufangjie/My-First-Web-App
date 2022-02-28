from db.session import engine#, get_db
from api.deps import get_db, models

if __name__ == "__main__":

    print(models.Base.metadata.tables.keys())
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(bind=engine)

    from datetime import date
    from core.security import get_password_hash

    lst = []
    for name, birth in zip(
            ["liubei", "guanyu", "zhangfei"],
            [date(161, 1, 1), date(162, 2, 2), date(165, 3, 3)]
    ):
        lst.append(models.User(username=name,
                               hashed_password=get_password_hash(name),
                               email=f"{name}@sanguo.com",
                               birth=birth,
                               sex=0,
                               phone="",
                               icon="",
        ))

    g = get_db()
    db = g.send(None)

    db.add_all(lst)

    db.commit() # need this?






# 刘备: 桃园结义
# 关羽: 不求同年同日生
# 张飞: 但求同年同日死
# 赞(刘备, 关羽, 张飞)

# 关羽: 斩颜良, 诛文丑, 猛气冲长缨
# 曹操: 勇冠三军
# 荀攸: 万人敌
# 关羽 回复 荀攸: 吾三弟于万军之中取上将首级如探囊取物
# 张飞:

# 关羽: 过五关, 斩六将, 千里走单骑
# 曹操: 曾经拥有过

# 张飞: 当阳一声吼, 渣渣退步走

# 关羽: 水淹七军
# 于禁: 投了
# 庞德: 头没了
# 刘备, 张飞, 诸葛亮, 曹操 觉得很赞

# 孟获: 南蛮入侵
# 诸葛亮: 七擒孟获
# 刘禅: 相父[赞]
