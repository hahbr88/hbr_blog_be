from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.post import Post, extract_first_image_url
from app.repositories.post_repo import PostRepo
from app.repositories.upload_repo import UploadRepo
from app.schemas.post import PostCreate, PostUpdate


def normalize_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    for t in tags:
        t2 = t.strip().lower()
        if not t2 or t2 in seen:
            continue
        seen.add(t2)
        out.append(t2)

    return out


class PostService:
    def __init__(self):
        self.repo = PostRepo()
        self.upload_repo = UploadRepo()

    # ✅ 공개 GET: 발행글만
    def list_public_posts(
        self, db: Session, *, q: str | None, skip: int, limit: int
    ) -> list[Post]:
        posts = self.repo.list(
            db, q=q, skip=skip, limit=limit, include_unpublished=False
        )
        self._apply_thumbnail_overrides(db, posts)
        return posts

    def get_public_post(self, db: Session, post_id: int) -> Post:
        post = self.repo.get(db, post_id, include_unpublished=False)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        self._apply_thumbnail_overrides(db, [post])
        return post

    # (기존 관리자/내부용 그대로)
    def list_posts(
        self, db: Session, *, q: str | None, skip: int, limit: int
    ) -> list[Post]:
        return self.repo.list(db, q=q, skip=skip, limit=limit, include_unpublished=True)

    def get_post(self, db: Session, post_id: int) -> Post:
        post = self.repo.get(db, post_id, include_unpublished=True)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def create_post(self, db: Session, data: PostCreate) -> Post:
        post = Post(
            title=data.title,
            content=data.content,
            is_published=True,
            is_temp=False,
            tags=normalize_tags(data.tags),
        )
        return self.repo.create(db, post)

    def create_temp_post(self, db: Session, data: PostCreate) -> Post:
        post = Post(
            title=data.title,
            content=data.content,
            is_published=False,
            is_temp=True,
            tags=normalize_tags(data.tags),
        )
        return self.repo.create(db, post)

    def update_post(self, db: Session, post_id: int, data: PostUpdate) -> Post:
        post = self.get_post(db, post_id)

        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        if data.tags is not None:
            post.tags = normalize_tags(data.tags)

        return self.repo.save(db, post)

    def delete_post(self, db: Session, post_id: int) -> None:
        post = self.get_post(db, post_id)
        post.is_deleted = True
        self.repo.save(db, post)

    def _apply_thumbnail_overrides(self, db: Session, posts: list[Post]) -> None:
        first_urls: dict[int, str] = {}
        for post in posts:
            url = extract_first_image_url(post.content)
            if url:
                first_urls[post.id] = url

        uploads = self.upload_repo.list_by_urls(db, set(first_urls.values()))
        by_url = {u.url: u.thumbnail_url for u in uploads}

        for post in posts:
            if post.id in first_urls:
                url = first_urls[post.id]
                setattr(post, "_thumbnail_override", by_url.get(url))
