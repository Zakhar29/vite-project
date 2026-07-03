// pages/UploadTrack.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/uploadTrack.css';

function UploadTrack() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    artist: 'Zakhar', // можно подтянуть из профиля
    genre: 'Synthwave',
    cover: null,
    coverPreview: 'https://picsum.photos/id/1015/300/300',
    duration: '',
    description: ''
  });

  const [isUploading, setIsUploading] = useState(false);

  const genres = [
    'Synthwave', 'Retrowave', 'Darksynth', 'Cyberpunk', 
    'Chillwave', 'Dreamwave', 'Outrun', 'Electro', 'Lo-fi'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCoverChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({
          ...prev,
          cover: file,
          coverPreview: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsUploading(true);

    // Здесь будет отправка на бэкенд или сохранение в localStorage
    // Пока имитируем задержку
    setTimeout(() => {
      // Сохраняем трек в localStorage (для демо)
      const existingTracks = JSON.parse(localStorage.getItem('userTracks') || '[]');
      const newTrack = {
        id: Date.now(),
        title: formData.title,
        artist: formData.artist,
        genre: formData.genre,
        cover: formData.coverPreview,
        duration: formData.duration || '3:30',
        description: formData.description,
        dateAdded: new Date().toISOString()
      };
      existingTracks.unshift(newTrack);
      localStorage.setItem('userTracks', JSON.stringify(existingTracks));
      
      setIsUploading(false);
      // Перенаправляем на профиль (или на страницу нового трека)
      navigate('/profile/me');
    }, 1500);
  };

  return (
    <div className="upload-page">
      <div className="upload-page__inner">
      <div className="upload-container">
        <h2 className="neon-title">🎧 ЗАГРУЗИТЬ ТРЕК</h2>
        
        <form onSubmit={handleSubmit}>
          {/* Обложка */}
          <div className="form-group">
            <label>Обложка трека</label>
            <div className="cover-upload">
              <img 
                src={formData.coverPreview} 
                alt="Cover preview" 
                className="cover-preview"
              />
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleCoverChange} 
                id="coverInput" 
              />
              <label htmlFor="coverInput" className="upload-cover-btn">
                Выбрать обложку
              </label>
            </div>
          </div>

          {/* Название трека */}
          <div className="form-group">
            <label>Название трека</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Neon Dreamscape Anthem"
              required
              className="neon-input"
            />
          </div>

          {/* Исполнитель (можно редактировать) */}
          <div className="form-group">
            <label>Исполнитель</label>
            <input
              type="text"
              name="artist"
              value={formData.artist}
              onChange={handleChange}
              placeholder="Zakhar"
              className="neon-input"
            />
          </div>

          {/* Жанр */}
          <div className="form-group">
            <label>Жанр</label>
            <select 
              name="genre" 
              value={formData.genre} 
              onChange={handleChange}
              className="neon-select"
            >
              {genres.map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>

          {/* Длительность (опционально) */}
          <div className="form-group">
            <label>Длительность (минуты:секунды)</label>
            <input
              type="text"
              name="duration"
              value={formData.duration}
              onChange={handleChange}
              placeholder="3:04"
              className="neon-input"
            />
          </div>

          {/* Описание / доп. информация */}
          <div className="form-group">
            <label>Описание (что-нибудь от себя)</label>
            <textarea
              name="description"
              rows="4"
              value={formData.description}
              onChange={handleChange}
              placeholder="Вдохновлён неоновыми огнями и ретро-футуризмом..."
              className="neon-textarea"
            />
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="neon-btn" 
              disabled={isUploading}
            >
              {isUploading ? 'ЗАГРУЗКА...' : '🚀 ОПУБЛИКОВАТЬ'}
            </button>
            <button 
              type="button" 
              className="cancel-btn" 
              onClick={() => navigate(-1)}
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
      </div>
    </div>
  );
}

export default UploadTrack;