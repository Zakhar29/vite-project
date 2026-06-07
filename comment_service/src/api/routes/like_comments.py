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

def get_comment_service() -> CommentService:
    return CommentService()

router = APIRouter(prefix="/comments", tags=["post-comments"])



@router.post("/{comment_id}/like", status_code=200)
async def like_comment(
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.like(comment_id, user.id)


@router.post("/{comment_id}/dislike", status_code=200)
async def dislike_comment(
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.dislike(comment_id, user.id)


@router.delete("/{comment_id}/like", status_code=200)
async def unlike_comment(
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.remove_like(comment_id, user.id)


@router.delete("/{comment_id}/dislike", status_code=200)
async def undislike_comment(
    comment_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return await service.remove_dislike(comment_id, user.id)