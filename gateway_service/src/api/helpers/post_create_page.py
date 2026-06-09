from typing import Optional



def extract_media_url(result) -> Optional[str]:
    """Извлекает URL из ответа media_service"""
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("url")
    if isinstance(result, dict):
        if "media" in result and result["media"]:
            return result["media"][0].get("url")
        if "url" in result:
            return result["url"]
    return None


def extract_full_key_from_url(url: str) -> Optional[str]:
    """
    Извлекает полный ключ из URL (с бакетом).
    Пример: http://localhost:9000/media-images/234/file.avif -> media-images/234/file.avif
    """
    match = re.search(r"http://[^/]+/(.+)", url)
    if match:
        return match.group(1)
    return None


def extract_post_id_from_key(key: str) -> Optional[str]:
    """Извлекает post_id из полного ключа"""
    parts = key.split("/")
    if len(parts) >= 2:
        return parts[1]
    return None
