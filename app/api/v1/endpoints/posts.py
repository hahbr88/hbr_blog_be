from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.post import PostCreate, PostUpdate, PostOut
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

# 🔒 쓰기만 토큰 필요
@router.post(
    "",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    return svc.create_post(db, payload)

@router.patch(
    "/{post_id}",
    response_model=PostOut,
    dependencies=[Depends(require_admin)],
)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    return svc.update_post(db, post_id, payload)

@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    svc.delete_post(db, post_id)
    return None
