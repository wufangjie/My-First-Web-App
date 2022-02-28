from fastapi import APIRouter

from app.api.v1.endpoints import (login,
                                  users,
                                  follow,
                                  thumb,
                                  blogs,
                                  pictures,
                                  comments,
                                  scan,
)


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(follow.router, prefix="/follow", tags=["follow"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
api_router.include_router(pictures.router, tags=["pictures"])
api_router.include_router(thumb.router, prefix="/thumb", tags=["thumb"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(scan.router, tags=["scan"])
