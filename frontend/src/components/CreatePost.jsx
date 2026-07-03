import { useState, useEffect } from 'react';
import Avatar from './Avatar';
import '../styles/createPost.css';

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function CreatePost({ isOpen, onClose, onPostCreated }) {
  const token = localStorage.getItem("access_token");

  const [userData, setUserData] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(true);

  const [text, setText] = useState('');
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [video, setVideo] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  // ========== Загрузка данных пользователя ==========

  useEffect(() => {
    if (isOpen && token) {
      loadUserData();
    }
  }, [isOpen, token]);

  const loadUserData = async () => {
    try {
      setIsLoadingUser(true);
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load user data');
      }

      const data = await response.json();
      setUserData(data);
    } catch (err) {
      console.error('Failed to load user data:', err);
      // Используем данные из localStorage как fallback
      setUserData({
        id: localStorage.getItem('user_id'),
        nickname: localStorage.getItem('nickname') || 'Пользователь',
        avatar_url: localStorage.getItem('avatar_url') || 'https://i.pravatar.cc/48'
      });
    } finally {
      setIsLoadingUser(false);
    }
  };

  if (!isOpen) return null;

  // ========== Обработка изображений ==========

  const handleImagesChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    if (images.length + files.length > 5) {
      setError('Максимум 5 изображений');
      return;
    }

    const newImages = [...images, ...files];
    setImages(newImages);

    const newPreviews = files.map(file => URL.createObjectURL(file));
    setImagePreviews([...imagePreviews, ...newPreviews]);
    setError(null);
  };

  const removeImage = (index) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = imagePreviews.filter((_, i) => i !== index);
    setImages(newImages);
    setImagePreviews(newPreviews);
  };

  // ========== Обработка видео ==========

  const handleVideoChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.size > 100 * 1024 * 1024) {
      setError('Видео не должно превышать 100MB');
      return;
    }

    setVideo(file);
    setVideoPreview(URL.createObjectURL(file));
    setError(null);
  };

  const removeVideo = () => {
    setVideo(null);
    setVideoPreview(null);
  };

  // ========== Отправка поста ==========

  const handlePublish = async () => {
    if (!text.trim() && images.length === 0 && !video) {
      setError('Добавьте текст или медиа');
      return;
    }

    setIsSubmitting(true);
    setUploadProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('text', text);

      images.forEach((image) => {
        formData.append('images', image);
      });

      if (video) {
        formData.append('video', video);
      }

      const response = await fetch(`${API_URL}/api/v1/post/create`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        credentials: 'include',
        body: formData
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Необходимо авторизоваться');
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка создания поста');
      }

      const data = await response.json();

      setUploadProgress(100);

      // Создаем объект поста с данными автора
      const newPost = {
        ...data.post,
        author: {
          id: userData?.id || localStorage.getItem('user_id'),
          nickname: userData?.nickname || localStorage.getItem('nickname') || 'Пользователь',
          avatar_url: userData?.avatar_url || localStorage.getItem('avatar_url') || 'https://i.pravatar.cc/48'
        },
        created_at: new Date().toISOString(),
        created_at_formatted: 'только что',
        likes_quantity: 0,
        comments_quantity: 0,
        is_liked: false
      };

      if (onPostCreated) {
        onPostCreated(newPost);
      }

      setTimeout(() => {
        resetForm();
        onClose();
      }, 500);

    } catch (err) {
      console.error('Failed to create post:', err);
      setError(err.message || 'Не удалось создать пост');
    } finally {
      setIsSubmitting(false);
    }
  };

  // ========== Сброс формы ==========

  const resetForm = () => {
    setText('');
    setImages([]);
    setImagePreviews([]);
    setVideo(null);
    setVideoPreview(null);
    setIsSubmitting(false);
    setUploadProgress(0);
    setError(null);
  };

  const handleClose = () => {
    if (!isSubmitting) {
      resetForm();
      onClose();
    }
  };

  // ========== Отрисовка ==========

  return (
    <div className="create-post-overlay" onClick={handleClose}>
      <div className="create-post-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="create-post-header">
          <div className="user-info">
            <div className="avatar">
              <Avatar
                src={userData?.avatar_url || localStorage.getItem('avatar_url')}
                alt={userData?.nickname || 'User'}
              />
            </div>
            <div>
              <p>{userData?.nickname || localStorage.getItem('nickname') || 'Пользователь'}</p>
              <span className="time">только что</span>
            </div>
          </div>
          <button
            className="close-btn"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            ✕
          </button>
        </div>

        {/* Ошибка */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Текст */}
        <div className="create-post-text">
          <textarea
            placeholder="Что у вас нового? Расскажите о музыке, поделитесь мыслями..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={isSubmitting}
            rows="4"
          />
        </div>

        {/* Превью изображений */}
        {imagePreviews.length > 0 && (
          <div className="image-previews">
            {imagePreviews.map((preview, index) => (
              <div key={index} className="image-preview-wrapper">
                <img src={preview} alt={`Preview ${index + 1}`} />
                <button
                  className="remove-media-btn"
                  onClick={() => removeImage(index)}
                  disabled={isSubmitting}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Превью видео */}
        {videoPreview && (
          <div className="video-preview-wrapper">
            <video src={videoPreview} controls className="video-preview" />
            <button
              className="remove-media-btn"
              onClick={removeVideo}
              disabled={isSubmitting}
            >
              ✕
            </button>
          </div>
        )}

        {/* Загрузка медиа */}
        <div className="create-post-media">
          <label className="media-upload-btn">
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleImagesChange}
              hidden
              disabled={isSubmitting || images.length >= 5}
            />
            📷 Фото ({images.length}/5)
          </label>

          <label className="media-upload-btn">
            <input
              type="file"
              accept="video/*"
              onChange={handleVideoChange}
              hidden
              disabled={isSubmitting || video !== null}
            />
            🎬 Видео {video && '✓'}
          </label>
        </div>

        {/* Прогресс загрузки */}
        {isSubmitting && (
          <div className="upload-progress">
            <div
              className="progress-bar"
              style={{ width: `${uploadProgress}%` }}
            />
            <span className="progress-text">
              {uploadProgress < 100 ? 'Загрузка...' : 'Готово!'}
            </span>
          </div>
        )}

        {/* Footer */}
        <div className="create-post-footer">
          <div className="made-with">
            Made with <span className="violet">V</span>
          </div>

          <div className="footer-right">
            <button
              className="publish-btn"
              onClick={handlePublish}
              disabled={isSubmitting || (!text.trim() && images.length === 0 && !video)}
            >
              {isSubmitting ? 'Публикация...' : 'Опубликовать'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreatePost;