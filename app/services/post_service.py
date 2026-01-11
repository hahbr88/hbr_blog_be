from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.post import Post
from app.repositories.post_repo import PostRepo
from app.schemas.post import PostCreate, PostUpdate

class PostService:
    def __init__(self):
        self.repo = PostRepo()

    def list_posts(self, db: Session, *, q: str | None, skip: int, limit: int) -> list[Post]:
        return self.repo.list(db, q=q, skip=skip, limit=limit)

    def get_post(self, db: Session, post_id: int) -> Post:
        post = self.repo.get(db, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def create_post(self, db: Session, data: PostCreate) -> Post:
        post = Post(title=data.title, content=data.content)
        return self.repo.create(db, post)

    def update_post(self, db: Session, post_id: int, data: PostUpdate) -> Post:
        post = self.get_post(db, post_id)

        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        if data.is_published is not None:
            post.is_published = data.is_published

        return self.repo.save(db, post)

    def delete_post(self, db: Session, post_id: int) -> None:
        post = self.get_post(db, post_id)
        post.is_deleted = True
        self.repo.save(db, post)
        