from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.dependencies import get_current_user, CurrentUser, get_comment_client
from src.clients.comments_service import CommentClient

router = APIRouter(prefix="/comments", tags=["Comment Actions"])


def _extract_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    return token


@router.post("/{comment_id}/like")
async def like_comment(
    request: Request,
    comment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    comment_client: CommentClient = Depends(get_comment_client),
):
    token = _extract_token(request)
    return await comment_client.like_comment(comment_id, token)


@router.post("/{comment_id}/unlike")
async def unlike_comment(
    request: Request,
    comment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    comment_client: CommentClient = Depends(get_comment_client),
):
    token = _extract_token(request)
    return await comment_client.unlike_comment(comment_id, token)


@router.post("/{comment_id}/dislike")
async def dislike_comment(
    request: Request,
    comment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    comment_client: CommentClient = Depends(get_comment_client),
):
    token = _extract_token(request)
    return await comment_client.dislike_comment(comment_id, token)


@router.post("/{comment_id}/undislike")
async def undislike_comment(
    request: Request,
    comment_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    comment_client: CommentClient = Depends(get_comment_client),
):
    token = _extract_token(request)
    return await comment_client.undislike_comment(comment_id, token)
