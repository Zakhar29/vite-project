// pages/ProfileEdit.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/profileEdit.css';

function ProfileEdit() {
  const navigate = useNavigate();

  // Загружаем текущие данные профиля из localStorage или используем значения по умолчанию
  const [formData, setFormData] = useState({
    avatar: localStorage.getItem('profileAvatar') || 'https://i.pravatar.cc/100',
    name: localStorage.getItem('profileName') || 'ZAKHAR',
    bio: localStorage.getItem('profileBio') || 'Преданный своему делу продюсер и диджей создает яркие звуковые ландшафты в стиле синтвейв.'
  });

  const [avatarPreview, setAvatarPreview] = useState(formData.avatar);

  // Обработчик изменения текстовых полей
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Обработчик загрузки аватара
  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result;
        setAvatarPreview(base64);
        setFormData(prev => ({ ...prev, avatar: base64 }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Сохранение в localStorage и возврат на страницу профиля
  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem('profileAvatar', formData.avatar);
    localStorage.setItem('profileName', formData.name);
    localStorage.setItem('profileBio', formData.bio);
    // Перенаправляем на профиль текущего пользователя (у вас id может быть динамическим)
    navigate('/profile/me'); // или просто '/profile/1', как вам удобнее
  };

  const handleCancel = () => {
    navigate(-1);
  };

  return (
    <div className="profile-edit-page">
      <div className="edit-form-container neon-border">
        <h2>Редактирование профиля</h2>
        <form onSubmit={handleSubmit}>
          {/* Аватар */}
          <div className="form-group">
            <label>Аватар</label>
            <div className="avatar-upload">
              <img src={avatarPreview} alt="Avatar preview" className="edit-avatar-preview" />
              <input type="file" accept="image/*" onChange={handleAvatarChange} id="avatarInput" />
              <label htmlFor="avatarInput" className="upload-btn">Выбрать фото</label>
            </div>
          </div>

          {/* Имя */}
          <div className="form-group">
            <label>Отображаемое имя</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Ваше имя"
              className="neon-input"
            />
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
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="save-btn neon-btn">Сохранить</button>
            <button type="button" onClick={handleCancel} className="cancel-btn">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProfileEdit;