from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])
svc = PostService()

@router.get("", response_model=list[PostOut])
def list_posts(
    q: str | None = Query(default=None, description="title search"),
    skip: int = 0,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return svc.list_posts(db, q=q, skip=skip, limit=limit)

@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    return svc.create_post(db, payload)

@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    return svc.get_post(db, post_id)

@router.patch("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    return svc.update_post(db, post_id, payload)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    svc.delete_post(db, post_id)
    return None
