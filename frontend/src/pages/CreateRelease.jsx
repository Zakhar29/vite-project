import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/createRelease.css';

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function CreateRelease() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [releaseType, setReleaseType] = useState('single');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // ========== Данные из API ==========
  const [albumTypes, setAlbumTypes] = useState([]);
  const [genres, setGenres] = useState([]);

  const [formData, setFormData] = useState({
    title: '',
    cover: null,
    coverPreview: 'https://picsum.photos/300/300',
    description: '',
    tracks: []
  });

  // ========== Загрузка справочных данных ==========

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    loadFormData();
  }, []);

  const loadFormData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/new_album/create-form-data`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка загрузки данных');
      }

      const data = await response.json();

      // Сохраняем жанры и типы
      setAlbumTypes(data.album_types || []);
      setGenres(data.genres || []);

      // Инициализируем треки с учётом типа
      initializeTracks('single');

    } catch (err) {
      console.error('Ошибка загрузки:', err);
      setError('Не удалось загрузить данные для создания релиза');
    } finally {
      setIsLoading(false);
    }
  };

  // ========== Вспомогательные функции ==========

  const getTypeName = () => {
    if (releaseType === 'single') return 'Сингл';
    if (releaseType === 'ep') return 'EP';
    return 'Альбом';
  };

  const getMaxTracks = () => {
    if (releaseType === 'single') return 2;
    if (releaseType === 'ep') return 6;
    return 30;
  };

  const getTypeId = () => {
    const typeMap = {
      'single': 2,
      'ep': 3,
      'album': 1
    };
    return typeMap[releaseType] || 1;
  };

  const initializeTracks = (type) => {
    const count = type === 'single' ? 1 : 2;
    const initialTracks = Array.from({ length: count }, (_, i) => ({
      id: Date.now() + i,
      title: '',
      audioFile: null,
      bpm: '',
      text: '',
      genreIds: [],
      author_attention: false
    }));
    setFormData(prev => ({ ...prev, tracks: initialTracks }));
  };

  // ========== Обработчики изменения типа ==========

  const handleTypeChange = (type) => {
    setReleaseType(type);
    initializeTracks(type);
  };

  // ========== Обработчики треков ==========

  const addTrack = () => {
    if (formData.tracks.length >= getMaxTracks()) {
      alert(`Максимум ${getMaxTracks()} треков для ${getTypeName()}`);
      return;
    }

    setFormData(prev => ({
      ...prev,
      tracks: [...prev.tracks, {
        id: Date.now(),
        title: '',
        audioFile: null,
        bpm: '',
        text: '',
        genreIds: [],
        author_attention: false
      }]
    }));
  };

  const removeTrack = (trackId) => {
    if (releaseType === 'single' && formData.tracks.length === 1) return;
    setFormData(prev => ({
      ...prev,
      tracks: prev.tracks.filter(t => t.id !== trackId)
    }));
  };

  const updateTrack = (trackId, field, value) => {
    setFormData(prev => ({
      ...prev,
      tracks: prev.tracks.map(t => t.id === trackId ? { ...t, [field]: value } : t)
    }));
  };

  // ========== Обработчики файлов ==========

  const handleCoverChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({ ...prev, cover: file, coverPreview: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  // ========== Отправка на сервер ==========

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // ===== Валидация =====
    if (!formData.title.trim()) {
      alert('Введите название релиза');
      return;
    }

    if (!formData.cover) {
      alert('Выберите обложку релиза');
      return;
    }

    if (formData.tracks.some(t => !t.title.trim() || !t.audioFile)) {
      alert('Заполните название и загрузите аудиофайл для каждого трека');
      return;
    }

    if (formData.tracks.some(t => !t.bpm)) {
      alert('Укажите BPM для каждого трека');
      return;
    }

    if (!token) {
      alert('Необходимо войти в систему');
      navigate('/login');
      return;
    }

    setIsSubmitting(true);

    try {
      const formDataObj = buildFormData();

      const response = await fetch(`${API_URL}/api/v1/new_album/create`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formDataObj,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка создания релиза');
      }

      const result = await response.json();

      alert('Релиз успешно создан и опубликован! 🎉');
      navigate(`/album/${result.album_id}`);

    } catch (err) {
      console.error('Ошибка создания релиза:', err);
      setError(err.message || 'Ошибка при создании релиза');
      alert(`Ошибка: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // ===== Формирование FormData для BFF =====

  const buildFormData = () => {
    const formDataObj = new FormData();

    // Основные поля
    formDataObj.append('title', formData.title.trim());
    formDataObj.append('type', String(getTypeId()));
    formDataObj.append('cover', formData.cover);
    formDataObj.append('tracks_count', String(formData.tracks.length));

    // Треки
    formData.tracks.forEach((track, index) => {
      formDataObj.append(`track_${index}_title`, track.title.trim());
      formDataObj.append(`track_${index}_bpm`, track.bpm);
      formDataObj.append(`track_${index}_genres`, JSON.stringify(track.genreIds));
      formDataObj.append(`track_${index}_text`, track.text || '');
      formDataObj.append(`track_${index}_author_attention`, String(track.author_attention));
      formDataObj.append(`track_${index}_file`, track.audioFile);
    });

    return formDataObj;
  };

  // ========== Состояние загрузки ==========

  if (isLoading) {
    return (
      <div className="create-release-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Загрузка данных...</p>
        </div>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="create-release-page">
      <div className="create-release-container neon-border">
        <h1 className="neon-title">Создать релиз</h1>

        {error && (
          <div className="error-message">{error}</div>
        )}

        <div className="release-type-switch">
          <button
            className={releaseType === 'single' ? 'active' : ''}
            onClick={() => handleTypeChange('single')}
          >
            Сингл
          </button>
          <button
            className={releaseType === 'ep' ? 'active' : ''}
            onClick={() => handleTypeChange('ep')}
          >
            EP
          </button>
          <button
            className={releaseType === 'album' ? 'active' : ''}
            onClick={() => handleTypeChange('album')}
          >
            Альбом
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Обложка */}
          <div className="form-group">
            <label>Обложка релиза *</label>
            <div className="cover-upload">
              <img src={formData.coverPreview} alt="cover" className="cover-preview" />
              <input
                type="file"
                accept="image/*"
                onChange={handleCoverChange}
                id="coverUpload"
                hidden
                required
              />
              <label htmlFor="coverUpload" className="upload-cover-btn">
                Выбрать изображение
              </label>
            </div>
          </div>

          {/* Название */}
          <div className="form-group">
            <label>Название {getTypeName().toLowerCase()} *</label>
            <input
              type="text"
              value={formData.title}
              onChange={e => setFormData({...formData, title: e.target.value})}
              required
              className="neon-input"
              placeholder="Введите название релиза"
            />
          </div>

          {/* Треки */}
          <div className="tracks-section">
            <div className="tracks-header">
              <h3>Треки ({formData.tracks.length} / {getMaxTracks()})</h3>
              {(releaseType !== 'single' || formData.tracks.length < 2) && (
                <button type="button" onClick={addTrack} className="add-track-btn">
                  + Добавить трек
                </button>
              )}
            </div>

            {formData.tracks.map((track, idx) => (
              <div key={track.id} className="track-editor neon-border">
                <div className="track-header">
                  <span>Трек {idx + 1}</span>
                  {formData.tracks.length > 1 && (
                    <button type="button" onClick={() => removeTrack(track.id)} className="remove-track">
                      ✖ Удалить
                    </button>
                  )}
                </div>

                <div className="form-group">
                  <label>Название трека *</label>
                  <input
                    type="text"
                    value={track.title}
                    onChange={e => updateTrack(track.id, 'title', e.target.value)}
                    required
                    className="neon-input"
                  />
                </div>

                <div className="form-group audio-upload">
                  <label>Аудиофайл *</label>
                  <div className="custom-file-upload">
                    <input
                      type="file"
                      accept="audio/*"
                      onChange={e => {
                        const file = e.target.files[0];
                        if (file) updateTrack(track.id, 'audioFile', file);
                      }}
                      id={`audio-${track.id}`}
                      hidden
                      required
                    />
                    <label htmlFor={`audio-${track.id}`} className="audio-upload-btn">
                      {track.audioFile ? '✓ Файл загружен' : 'Выбрать аудиофайл'}
                    </label>
                  </div>
                </div>

                <div className="form-group">
                  <label>BPM (темп) *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={track.bpm}
                    onChange={e => updateTrack(track.id, 'bpm', e.target.value)}
                    placeholder="128.00"
                    className="neon-input"
                    required
                  />
                </div>

                {/* Жанры — из загруженных данных */}
                <div className="form-group genres-select">
                  <label>Жанры (можно несколько)</label>
                  <select
                    multiple
                    value={track.genreIds}
                    onChange={e => {
                      const selected = Array.from(e.target.selectedOptions, opt => Number(opt.value));
                      updateTrack(track.id, 'genreIds', selected);
                    }}
                    className="neon-select"
                  >
                    {genres.map(g => (
                      <option key={g.id} value={g.id}>{g.title}</option>
                    ))}
                  </select>
                  <small>Удерживайте Ctrl (или Cmd) для выбора нескольких жанров</small>
                </div>

                <div className="form-group">
                  <label>Текст песни (опционально)</label>
                  <textarea
                    rows="3"
                    value={track.text}
                    onChange={e => updateTrack(track.id, 'text', e.target.value)}
                    className="neon-textarea"
                    placeholder="Введите текст песни..."
                  />
                </div>

                <div className="form-group checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={track.author_attention}
                      onChange={e => updateTrack(track.id, 'author_attention', e.target.checked)}
                    />
                    Авторское внимание (выделить трек)
                  </label>
                </div>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="neon-btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Публикация...' : 'Опубликовать релиз'}
            </button>
            <button type="button" onClick={() => navigate(-1)} className="cancel-btn">
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateRelease;