from datetime import datetime
from config import MediaType, MediaPath


class MediaService:
    def __init__(self, minio_client, cdn_domain: str = "cdn.music-social.com"):
        self.client = minio_client
        self.cdn_domain = cdn_domain

    def get_track_path(self, album_id: str, track_number: int, format: str = "aac") -> MediaPath:
        """Путь для трека"""
        key = f"albums/{album_id}/track_{track_number}.{format}"
        return MediaPath(
            bucket=MediaType.TRACK.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.TRACK.value}/{key}"
        )

    def get_album_cover_path(self, album_id: str, size: str) -> MediaPath:
        """Путь для обложки альбома"""
        key = f"{album_id}/cover_{size}.avif"
        return MediaPath(
            bucket=MediaType.COVER.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.COVER.value}/{key}"
        )

    def get_avatar_path(self, user_id: str, size: str) -> MediaPath:
        """Путь для аватарки пользователя"""

        key = f"{user_id}/{size}.avif"
        return MediaPath(
            bucket=MediaType.AVATAR.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.AVATAR.value}/{key}"
        )

    def get_chat_image_path(self, chat_id: str, message_id: str, image_name: str, format: str = "avif") -> MediaPath:
        """Путь для изображения в чате"""
        key = f"{chat_id}/{message_id}/{image_name}.{format}"
        return MediaPath(
            bucket=MediaType.CHAT_IMAGE.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.CHAT_IMAGE.value}/{key}",
        )

    def get_chat_video_path(self, chat_id: str, message_id: str, video_name: str, format: str = "mp4") -> MediaPath:
        """Путь для видео в чате"""
        key = f"{chat_id}/{message_id}/{video_name}.{format}"
        return MediaPath(
            bucket=MediaType.CHAT_VIDEO.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.CHAT_VIDEO.value}/{key}",
        )

    def get_chat_audio_message_path(self, chat_id: str, message_id: str, format: str = "ogg") -> MediaPath:
        """Путь для аудио сообщения"""
        key = f"{chat_id}/{message_id}_audio_{int(datetime.now().timestamp())}.{format}"
        return MediaPath(
            bucket=MediaType.CHAT_AUDIO.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.CHAT_AUDIO.value}/{key}",
        )

    def get_post_image_path(self, post_id: str, image_name: str, format: str = "avif") -> MediaPath:
        """Путь для изображения в посте"""
        key = f"{post_id}/{image_name}.{format}"
        return MediaPath(
            bucket=MediaType.IMAGE.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.IMAGE.value}/{key}",
        )

    def get_post_video_path(self, post_id: str, video_name: str, format: str = "mp4") -> MediaPath:
        """Путь для видео в посте"""
        key = f"{post_id}/{video_name}.{format}"
        return MediaPath(
            bucket=MediaType.VIDEO.value,
            key=key,
            url=f"http://{self.cdn_domain}/{MediaType.VIDEO.value}/{key}",
        )
