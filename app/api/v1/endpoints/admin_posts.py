from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.post import PostCreate, PostOut, PostUpdate
from app.services.post_service import PostService

router = APIRouter(prefix="/admin/posts", tags=["admin"])
svc = PostService()


# 🔒 관리자: 생성
@router.post(
    "",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    return svc.create_post(db, payload)


# 🔒 관리자: 수정
@router.patch(
    "/{post_id}",
    response_model=PostOut,
    dependencies=[Depends(require_admin)],
)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    return svc.update_post(db, post_id, payload)


# 🔒 관리자: 삭제
@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    svc.delete_post(db, post_id)
    return None


# (선택) 관리자 목록/상세: draft 포함 보고 싶으면 서비스에 admin용 메서드 추가해서 여기 넣기
# @router.get("", response_model=list[PostOut], dependencies=[Depends(require_admin)])
# def list_posts_admin(...):
#     return svc.list_all_posts(...)
