from fastapi import APIRouter

# from app.api.v1.endpoints.posts import router as posts_router
from app.api.v1.endpoints import admin_posts, posts, uploads

api_router = APIRouter()
api_router.include_router(posts.router)
api_router.include_router(admin_posts.router)
api_router.include_router(uploads.router)
