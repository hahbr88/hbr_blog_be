from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.post import PostOut
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])
svc = PostService()

# ✅ 공개 GET: 발행글만
@router.get("", response_model=list[PostOut])
def list_posts(
    q: str | None = Query(default=None, description="title search"),
    skip: int = 0,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return svc.list_public_posts(db, q=q, skip=skip, limit=limit)

@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    return svc.get_public_post(db, post_id)
