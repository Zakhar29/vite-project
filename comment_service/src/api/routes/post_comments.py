from typing import Annotated, Optional
from fastapi import APIRouter, Body, Depends, Query, status

from src.api.dependencies import CurrentUser, get_current_user
from src.api.schemas import (
    PostCommentCreate,
    PostCommentListResponse,
    PostCommentResponse,
    PostCommentUpdate,
)
from src.services.comment_service import CommentService

router = APIRouter(prefix="/posts", tags=["post-comments"])


def get_comment_service() -> CommentService:
    return CommentService()


@router.get(
    "/{post_id}/comments",
    response_model=PostCommentListResponse,
    summary="Список комментариев к посту",
)
async def list_post_comments(
    post_id: str,
    root_only: bool = Query(True, description="Только корневые комментарии"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|rating_quantity)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    service: CommentService = Depends(get_comment_service),
):
    items, total = await service.list_for_entity(
        "post", post_id,
        root_only=root_only,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return PostCommentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post(
    "/{post_id}/comments",
    response_model=PostCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Комментарий к посту",
)
async def create_post_comment(
    post_id: str,
    data: Annotated[
        PostCommentCreate,
        Body(openapi_examples={"default": {"value": {"comment": "Отличный пост!"}}}),
    ],
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.create(
        user.id,
        entity_type="post",
        entity_id=post_id,
        comment=data.comment,
    )


@router.get(
    "/{post_id}/comments/{comment_id}",
    response_model=PostCommentResponse,
    summary="Комментарий к посту по ID",
)
async def get_post_comment(
    post_id: str,
    comment_id: str,
    service: CommentService = Depends(get_comment_service),
):
    return await service.get_for_entity(comment_id, "post", post_id)


@router.get(
    "/{post_id}/comments/{comment_id}/replies",
    response_model=PostCommentListResponse,
    summary="Ответы на комментарий к посту",
)
async def list_post_comment_replies(
    post_id: str,
    comment_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|rating_quantity)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    service: CommentService = Depends(get_comment_service),
):
    items, total = await service.list_for_entity(
        "post", post_id,
        answer_id=comment_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return PostCommentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.put(
    "/{post_id}/comments/{comment_id}",
    response_model=PostCommentResponse,
    summary="Изменить комментарий к посту",
)
async def update_post_comment(
    post_id: str,
    comment_id: str,
    data: PostCommentUpdate,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.update(
        comment_id,
        user.id,
        "post",
        post_id,
        comment=data.comment,
    )


@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить комментарий к посту",
)
async def delete_post_comment(
    post_id: str,
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    await service.delete(comment_id, user.id, "post", post_id)
