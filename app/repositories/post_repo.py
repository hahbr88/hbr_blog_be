from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.post import Post

class PostRepo:
    def list(self, db: Session, *, q: str | None, skip: int, limit: int) -> list[Post]:
        stmt = select(Post).where(Post.is_deleted == False)  # noqa: E712
        if q:
            stmt = stmt.where(Post.title.contains(q))
        stmt = stmt.order_by(Post.id.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get(self, db: Session, post_id: int) -> Post | None:
        stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)  # noqa: E712
        return db.execute(stmt).scalars().first()

    def create(self, db: Session, post: Post) -> Post:
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    def save(self, db: Session, post: Post) -> Post:
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
