import { useState, useEffect } from 'react';
import '../styles/createPostModal.css';

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

const AVAILABLE_REACTIONS = ['🔥', '❤️', '👽', '🎧', '💿', '✨', '🎸', '🕹️', '👍', '😎'];

function CreatePostModal({ isOpen, onClose, onPostCreated }) {
  const token = localStorage.getItem("access_token");

  const [userData, setUserData] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(true);

  const [text, setText] = useState('');
  const [selectedReactions, setSelectedReactions] = useState(['🔥']);
  const [isSubmitting, setIsSubmitting] = useState(false);
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

  // ========== Обработчики ==========

  const toggleReaction = (emoji) => {
    setSelectedReactions(prev =>
      prev.includes(emoji)
        ? prev.filter(e => e !== emoji)
        : [...prev, emoji]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Введите текст поста');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/post/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        credentials: 'include',
        body: JSON.stringify({
          text: text,
          reactions: selectedReactions
        })
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Необходимо авторизоваться');
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка создания поста');
      }

      const data = await response.json();

      if (onPostCreated) {
        onPostCreated(data.post);
      }

      // Сброс и закрытие
      setText('');
      setSelectedReactions(['🔥']);
      onClose();

    } catch (err) {
      console.error('Failed to create post:', err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content neon-border" onClick={(e) => e.stopPropagation()}>
        {/* Header с информацией о пользователе */}
        <div className="modal-header">
          <div className="user-info">
            <img
              src={userData?.avatar_url || localStorage.getItem('avatar_url') || 'https://i.pravatar.cc/48'}
              alt={userData?.nickname || 'User'}
              className="user-avatar"
            />
            <div>
              <span className="user-name">
                {userData?.nickname || localStorage.getItem('nickname') || 'Пользователь'}
              </span>
              <span className="user-status">создает пост</span>
            </div>
          </div>
          <button
            className="modal-close-btn"
            onClick={onClose}
            disabled={isSubmitting}
          >
            ✕
          </button>
        </div>

        <h3 className="modal-title">✨ Создать пост</h3>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <textarea
            className="post-textarea neon-textarea"
            placeholder="Что у вас нового? Например: «Скоро будет дроп !!!»"
            rows="4"
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={isSubmitting}
            autoFocus
          />

          <div className="reactions-picker">
            <label>Выберите реакции (можно несколько):</label>
            <div className="emoji-grid">
              {AVAILABLE_REACTIONS.map(emoji => (
                <span
                  key={emoji}
                  className={`emoji-option ${selectedReactions.includes(emoji) ? 'active' : ''}`}
                  onClick={() => toggleReaction(emoji)}
                >
                  {emoji}
                </span>
              ))}
            </div>
            {selectedReactions.length > 0 && (
              <div className="selected-reactions">
                Выбрано: {selectedReactions.join(' ')}
              </div>
            )}
          </div>

          <div className="modal-actions">
            <button
              type="submit"
              className="neon-btn-small"
              disabled={isSubmitting || !text.trim()}
            >
              {isSubmitting ? 'Публикация...' : 'Опубликовать'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="cancel-btn-small"
              disabled={isSubmitting}
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreatePostModal;