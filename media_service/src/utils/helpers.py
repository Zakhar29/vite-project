from PIL import Image
from moviepy import VideoFileClip
from pydub import AudioSegment
from fastapi import UploadFile
from typing import Optional
import os
import tempfile


async def convert_audio_to_aac256(input_file: UploadFile) -> tuple[Optional[bytes], str]:
    """
    Конвертация аудио в AAC 256 кбит/с

    Args:
        input_file: загруженный файл из FastAPI (UploadFile)

    Returns:
        (бинарные_данные_сконвертированного_файла, расширение_файла)
        Если ошибка: (None, сообщение_об_ошибке)
    """
    temp_input = None
    temp_output = None

    try:
        # 1. Сохраняем входной файл
        ext = input_file.filename.split('.')[-1] if input_file.filename else "wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            content = await input_file.read()
            tmp.write(content)
            temp_input = tmp.name

        # 2. Выходной файл: используем .m4a (стандартный контейнер для AAC)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
            temp_output = tmp.name

        # 3. Конвертируем через pydub
        audio = AudioSegment.from_file(temp_input)

        # 🔑 FIX: format=контейнер, codec=аудиокодек
        audio.export(
            temp_output,
            format="mp4",  # контейнер MP4/M4A
            codec="aac",  # аудиокодек AAC
            bitrate="256k",
            parameters=["-movflags", "+faststart"]  # опционально: для стриминга
        )

        # 4. Читаем результат в байты
        with open(temp_output, 'rb') as f:
            output_bytes = f.read()

        return output_bytes, "m4a"

    except Exception as e:
        return None, str(e)

    finally:
        # Чистим временные файлы
        for path in (temp_input, temp_output):
            if path and os.path.exists(path):
                os.unlink(path)


async def convert_image_to_avif_sizes(
        input_file: UploadFile,
        sizes: dict = None
) -> tuple[Optional[list[tuple[bytes, str, str]]], str]:
    """
    Конвертация изображения в 3 размера в формате AVIF

    Args:
        input_file: загруженный файл из FastAPI
        sizes: словарь с размерами {название: ширина}, по умолчанию:
               {"small": 320, "medium": 768, "large": 1280}

    Returns:
        список кортежей (бинарные_данные, расширение, название_размера)
        Например: [(bytes, "avif", "small"), (bytes, "avif", "medium"), ...]
        Если ошибка: (None, сообщение_об_ошибке)
    """
    if sizes is None:
        sizes = {
            "small": 100,
            "medium": 300,
            "large": 600
        }

    temp_input = None
    temp_outputs = []

    try:
        # Сохраняем входной файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_file.filename.split('.')[-1]}") as tmp:
            content = await input_file.read()
            tmp.write(content)
            temp_input = tmp.name

        # Открываем изображение
        with Image.open(temp_input) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img

            results = []

            # Создаём каждый размер
            for size_name, target_width in sizes.items():
                # Создаём временный файл для этого размера
                with tempfile.NamedTemporaryFile(delete=False, suffix=".avif") as tmp:
                    temp_output = tmp.name
                    temp_outputs.append(temp_output)

                # Вычисляем высоту с сохранением пропорций

                # Изменяем размер
                resized_img = img.resize((target_width, target_width), Image.Resampling.LANCZOS)

                # Сохраняем в AVIF
                resized_img.save(temp_output, format="AVIF", quality=85)

                # Читаем результат
                with open(temp_output, 'rb') as f:
                    output_bytes = f.read()

                results.append((output_bytes, "avif", size_name))

            return results, ""

    except Exception as e:
        return None, str(e)

    finally:
        if temp_input and os.path.exists(temp_input):
            os.unlink(temp_input)
        for tmp in temp_outputs:
            if os.path.exists(tmp):
                os.unlink(tmp)

async def convert_image_to_avif(
        input_file: UploadFile,
) -> tuple[Optional[list[tuple[bytes, str, str]]], str]:
    """
    Конвертация изображения в 3 размера в формате AVIF

    Args:
        input_file: загруженный файл из FastAPI
        sizes: словарь с размерами {название: ширина}, по умолчанию:
               {"small": 320, "medium": 768, "large": 1280}

    Returns:
        список кортежей (бинарные_данные, расширение, название_размера)
        Например: [(bytes, "avif", "small"), (bytes, "avif", "medium"), ...]
        Если ошибка: (None, сообщение_об_ошибке)
    """


    temp_input = None
    temp_outputs = []

    try:
        # Сохраняем входной файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_file.filename.split('.')[-1]}") as tmp:
            content = await input_file.read()
            tmp.write(content)
            temp_input = tmp.name

        # Открываем изображение
        with Image.open(temp_input) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img

            results = []

            # Создаём каждый размер
            with tempfile.NamedTemporaryFile(delete=False, suffix=".avif") as tmp:
                temp_output = tmp.name
                temp_outputs.append(temp_output)

            # Сохраняем в AVIF
            img.save(temp_output, format="AVIF", quality=85)

            # Читаем результат
            with open(temp_output, 'rb') as f:
                output_bytes = f.read()

            results.append((output_bytes, "avif"))

            return results, ""

    except Exception as e:
        return None, str(e)

    finally:
        if temp_input and os.path.exists(temp_input):
            os.unlink(temp_input)
        for tmp in temp_outputs:
            if os.path.exists(tmp):
                os.unlink(tmp)

async def convert_video_to_mp4_h264(
        input_file: UploadFile,
        max_height: int = 1080
) -> tuple[Optional[bytes], str]:
    """
    Конвертация видео в MP4 H.264 с аудио AAC 256 кбит/с

    Args:
        input_file: загруженный файл из FastAPI
        max_height: максимальная высота (720 или 1080)

    Returns:
        (бинарные_данные_сконвертированного_файла, расширение_файла)
        Если ошибка: (None, сообщение_об_ошибке)
    """
    temp_input = None
    temp_output = None

    try:
        # Сохраняем входной файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_file.filename.split('.')[-1]}") as tmp:
            content = await input_file.read()
            tmp.write(content)
            temp_input = tmp.name

        # Выходной файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            temp_output = tmp.name

        # Конвертируем через moviepy
        clip = VideoFileClip(temp_input)

        # Масштабируем если нужно
        if clip.h > max_height:
            new_height = max_height
            new_width = int(clip.w * (max_height / clip.h))
            new_width = new_width if new_width % 2 == 0 else new_width + 1
            clip = clip.resize(newsize=(new_width, new_height))

        # Экспортируем
        clip.write_videofile(
            temp_output,
            codec='libx264',
            audio_codec='aac',
            audio_bitrate='256k',
            preset='medium',
            logger=None
        )

        clip.close()

        # Читаем результат
        with open(temp_output, 'rb') as f:
            output_bytes = f.read()

        return output_bytes, "mp4"

    except Exception as e:
        return None, str(e)

    finally:
        if temp_input and os.path.exists(temp_input):
            os.unlink(temp_input)
        if temp_output and os.path.exists(temp_output):
            os.unlink(temp_output)


async def convert_video_multiple_versions(
        input_file: UploadFile,
        max_height: int = 1080
) -> tuple[Optional[list[tuple[bytes, str, str]]], str]:
    """
    Создаёт две версии видео: 720p и 1080p

    Args:
        input_file: загруженный файл из FastAPI
        max_height: максимальное разрешение видео

    Returns:
        список кортежей (бинарные_данные, расширение, название_версии)
        Например: [(bytes, "mp4", "720p"), (bytes, "mp4", "1080p")]
        Если ошибка: (None, сообщение_об_ошибке)
    """
    results = []

    heights = [
        ("144p", 144),
        ("240p", 240),
        ("360p", 360),
        ("480p", 480),
        ("720p", 720),
        ("1080p", 1080)
    ]

    for version, height in heights:
        # Пересоздаём файловый объект для каждой версии
        if height > max_height:
            break

        else:
            await input_file.seek(0)  # возвращаем курсор в начало

            output_bytes, ext = await convert_video_to_mp4_h264(input_file, max_height=height)

            if output_bytes is None:
                return None, f"Ошибка при конвертации в {version}"

            results.append((output_bytes, ext, version))

    return results, ""
