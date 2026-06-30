// pages/ProfileEdit.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/profileEdit.css';

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function ProfileEdit() {
  const navigate = useNavigate();

  const token = localStorage.getItem("access_token");

  // ========== Состояния ==========

  const [formData, setFormData] = useState({
    avatar: '',
    nickname: '',
    username: '',
    email: '',
    bio: '',
  });

  const [originalData, setOriginalData] = useState({});
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [serverError, setServerError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // ========== Загрузка данных пользователя ==========

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/user/settings/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка загрузки данных');
      }

      const data = await response.json();

      const userData = {
        avatar: data.avatar_url || '',
        nickname: data.nickname || '',
        username: data.username || '',
        email: data.email || '',
        bio: data.bio || '',
      };

      setFormData(userData);
      setOriginalData(userData);
      setAvatarPreview(data.avatar_url || '');
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      setServerError('Не удалось загрузить данные профиля');
    } finally {
      setIsLoading(false);
    }
  };

  // ========== Обработчики изменения полей ==========

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Очищаем сообщения при редактировании
    if (serverError) setServerError('');
    if (successMessage) setSuccessMessage('');
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // ========== Сохранение ==========

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Проверяем, что есть изменения
    const hasChanges = (
      formData.nickname !== originalData.nickname ||
      formData.username !== originalData.username ||
      formData.bio !== originalData.bio ||
      avatarFile !== null
    );

    if (!hasChanges) {
      setSuccessMessage('Нет изменений для сохранения');
      setTimeout(() => setSuccessMessage(''), 3000);
      return;
    }

    setIsSaving(true);
    setServerError('');
    setSuccessMessage('');

    try {
      // 1. Если загружен новый аватар — загружаем его первым
      let newAvatarUrl = formData.avatar;

      if (avatarFile) {
        const avatarFormData = new FormData();
        avatarFormData.append('file', avatarFile);

        const avatarResponse = await fetch(`${API_URL}/api/v1/user/settings/avatar`, {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: avatarFormData,
        });

        if (!avatarResponse.ok) {
          const errorData = await avatarResponse.json();
          throw new Error(errorData.detail || 'Ошибка загрузки аватара');
        }

        const avatarData = await avatarResponse.json();
        newAvatarUrl = avatarData.avatar_url;
      }

      // 2. Обновляем остальные поля по отдельности

      const updatePromises = [];

      // Никнейм
      if (formData.nickname !== originalData.nickname) {
        updatePromises.push(
          fetch(`${API_URL}/api/v1/user/settings/nickname`, {
            method: 'PUT',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nickname: formData.nickname }),
          })
        );
      }

      // Username
      if (formData.username !== originalData.username) {
        updatePromises.push(
          fetch(`${API_URL}/api/v1/user/settings/username`, {
            method: 'PUT',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: formData.username }),
          })
        );
      }

      // Био
      if (formData.bio !== originalData.bio) {
        updatePromises.push(
          fetch(`${API_URL}/api/v1/user/settings/bio`, {
            method: 'PUT',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ bio: formData.bio }),
          })
        );
      }

      // Ждём выполнения всех запросов
      const results = await Promise.allSettled(updatePromises);

      // Проверяем, были ли ошибки
      const errors = results.filter(r => r.status === 'rejected');
      if (errors.length > 0) {
        throw new Error('Ошибка при обновлении некоторых полей');
      }

      // Обновляем оригинальные данные
      setOriginalData({
        ...formData,
        avatar: newAvatarUrl,
      });

      // Обновляем avatar_url в localStorage (для Navbar)
      if (newAvatarUrl) {
        localStorage.setItem('userAvatar', newAvatarUrl);
      }

      setSuccessMessage('Профиль успешно обновлён!');
      setTimeout(() => {
        navigate('/profile/me');
      }, 1500);

    } catch (error) {
      console.error('Ошибка сохранения:', error);
      setServerError(error.message || 'Ошибка при сохранении профиля');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    navigate(-1);
  };

  // ========== Состояние загрузки ==========

  if (isLoading) {
    return (
      <div className="profile-edit-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Загрузка данных профиля...</p>
        </div>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="profile-edit-page">
      <div className="edit-form-container neon-border">
        <h2>Редактирование профиля</h2>

        {serverError && (
          <div className="error-message">{serverError}</div>
        )}

        {successMessage && (
          <div className="success-message">{successMessage}</div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Аватар */}
          <div className="form-group">
            <label>Аватар</label>
            <div className="avatar-upload">
              <img
                src={avatarPreview || '/default-avatar.png'}
                alt="Avatar preview"
                className="edit-avatar-preview"
              />
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                id="avatarInput"
              />
              <label htmlFor="avatarInput" className="upload-btn">
                Выбрать фото
              </label>
            </div>
            <span className="field-hint">Рекомендуемый размер: 500x500px</span>
          </div>

          {/* Никнейм */}
          <div className="form-group">
            <label>Отображаемое имя (никнейм) *</label>
            <input
              type="text"
              name="nickname"
              value={formData.nickname}
              onChange={handleChange}
              placeholder="Ваш никнейм"
              className="neon-input"
              disabled={isSaving}
              required
            />
          </div>

          {/* Username */}
          <div className="form-group">
            <label>Имя пользователя (username) *</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="username"
              className="neon-input"
              disabled={isSaving}
              required
            />
            <span className="field-hint">Только латиница, цифры и знак подчёркивания. 3–30 символов.</span>
          </div>

          {/* Email (только для просмотра) */}
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              className="neon-input"
              disabled
              style={{ opacity: 0.6, cursor: 'not-allowed' }}
            />
            <span className="field-hint">Email нельзя изменить. Обратитесь в поддержку.</span>
          </div>

          {/* Биография */}
          <div className="form-group">
            <label>О себе</label>
            <textarea
              name="bio"
              rows="5"
              value={formData.bio}
              onChange={handleChange}
              placeholder="Расскажите о себе..."
              className="neon-textarea"
              disabled={isSaving}
              maxLength="500"
            />
            <span className="field-hint">{formData.bio.length}/500 символов</span>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="save-btn neon-btn"
              disabled={isSaving}
            >
              {isSaving ? 'Сохранение...' : 'Сохранить'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="cancel-btn"
              disabled={isSaving}
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProfileEdit;