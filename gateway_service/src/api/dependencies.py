from src.clients.users_service import UsersClient
from src.clients.media_service import MediaClient
from src.clients.music_service import MusicClient
from src.clients.social_feed_service import SocialClient
from src.clients.comments_service import CommentClient


def get_users_client() -> UsersClient:
    return UsersClient()


def get_media_client() -> MediaClient:
    return MediaClient()


def get_music_client() -> MusicClient:
    return MusicClient()


def get_social_client() -> SocialClient:
    return SocialClient()


def get_comment_client() -> CommentClient:
    return CommentClient()