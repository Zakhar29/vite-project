import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/createRelease.css';

const AVAILABLE_GENRES = ['Synthwave', 'Retrowave', 'Darksynth', 'Cyberpunk', 'Chillwave', 'Dreamwave', 'Outrun', 'Electro', 'Lo-fi', 'Techno'];

function CreateRelease() {
  const navigate = useNavigate();
  const [releaseType, setReleaseType] = useState('single');

  const [formData, setFormData] = useState({
    title: '',
    artist: 'Zakhar',
    cover: null,
    coverPreview: 'https://picsum.photos/300/300',
    year: new Date().getFullYear(),
    description: '',
    tracks: []
  });

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

  const handleTypeChange = (type) => {
    setReleaseType(type);
    
    const count = type === 'single' ? 1 : 2;
    const initialTracks = Array.from({ length: count }, (_, i) => ({
      id: Date.now() + i,
      title: '',
      audioFile: null,
      duration: '',
      bpm: '',
      lyrics: '',
      genres: []
    }));

    setFormData(prev => ({ ...prev, tracks: initialTracks }));
  };

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
        duration: '', 
        bpm: '', 
        lyrics: '', 
        genres: [] 
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

  const handleAudioUpload = (trackId, file) => {
    if (!file) return;
    const audio = new Audio();
    audio.src = URL.createObjectURL(file);

    audio.addEventListener('loadedmetadata', () => {
      const minutes = Math.floor(audio.duration / 60);
      const seconds = Math.floor(audio.duration % 60);
      const duration = `${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
      updateTrack(trackId, 'duration', duration);
    });

    updateTrack(trackId, 'audioFile', file);
  };

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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title) return alert('Введите название релиза');
    if (formData.tracks.some(t => !t.title || !t.audioFile)) {
      return alert('Заполните название и загрузите аудиофайл для каждого трека');
    }

    const newRelease = {
      id: Date.now(),
      type: releaseType,
      title: formData.title,
      artist: formData.artist,
      cover: formData.coverPreview,
      year: formData.year,
      description: formData.description,
      tracks: formData.tracks
    };

    if (releaseType === 'single') {
      const existing = JSON.parse(localStorage.getItem('userSingles') || '[]');
      localStorage.setItem('userSingles', JSON.stringify([newRelease, ...existing]));
    } else {
      const existing = JSON.parse(localStorage.getItem('userAlbums') || '[]');
      localStorage.setItem('userAlbums', JSON.stringify([newRelease, ...existing]));
    }

    navigate('/profile/me');
  };

  return (
    <div className="create-release-page">
      <div className="create-release-container neon-border">
        <h1 className="neon-title">Создать релиз</h1>

        <div className="release-type-switch">
          <button className={releaseType === 'single' ? 'active' : ''} onClick={() => handleTypeChange('single')}>Сингл</button>
          <button className={releaseType === 'ep' ? 'active' : ''} onClick={() => handleTypeChange('ep')}>EP</button>
          <button className={releaseType === 'album' ? 'active' : ''} onClick={() => handleTypeChange('album')}>Альбом</button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Обложка */}
          <div className="form-group">
            <label>Обложка релиза</label>
            <div className="cover-upload">
              <img src={formData.coverPreview} alt="cover" className="cover-preview" />
              <input type="file" accept="image/*" onChange={handleCoverChange} id="coverUpload" hidden />
              <label htmlFor="coverUpload" className="upload-cover-btn">Выбрать изображение</label>
            </div>
          </div>

          <div className="form-group">
            <label>Название {getTypeName().toLowerCase()}</label>
            <input type="text" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} required className="neon-input" />
          </div>

          <div className="form-group">
            <label>Исполнитель</label>
            <input type="text" value={formData.artist} onChange={e => setFormData({...formData, artist: e.target.value})} className="neon-input" />
          </div>

          <div className="form-group">
            <label>Год выпуска</label>
            <input type="number" value={formData.year} onChange={e => setFormData({...formData, year: e.target.value})} className="neon-input" />
          </div>

          <div className="form-group">
            <label>Описание</label>
            <textarea rows="3" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="neon-textarea" />
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
                    <button type="button" onClick={() => removeTrack(track.id)} className="remove-track">✖ Удалить</button>
                  )}
                </div>

                <div className="form-group">
                  <label>Название трека</label>
                  <input type="text" value={track.title} onChange={e => updateTrack(track.id, 'title', e.target.value)} required className="neon-input" />
                </div>

                {/* Аудиофайл */}
                <div className="form-group audio-upload">
                  <label>Аудиофайл</label>
                  <div className="custom-file-upload">
                    <input 
                      type="file" 
                      accept="audio/*" 
                      onChange={e => handleAudioUpload(track.id, e.target.files[0])} 
                      id={`audio-${track.id}`} 
                      hidden 
                    />
                    <label htmlFor={`audio-${track.id}`} className="audio-upload-btn">
                      {track.audioFile ? '✓ Файл загружен' : 'Выбрать аудиофайл'}
                    </label>
                  </div>
                  {track.duration && <span className="duration">Длительность: {track.duration}</span>}
                </div>

                {/* BPM */}
                <div className="form-group">
                  <label>BPM (темп)</label>
                  <input 
                    type="number" 
                    step="0.01" 
                    value={track.bpm} 
                    onChange={e => updateTrack(track.id, 'bpm', e.target.value)} 
                    placeholder="128.00" 
                    className="neon-input" 
                  />
                </div>

                {/* Жанры */}
                <div className="form-group genres-select">
                  <label>Жанры (можно несколько)</label>
                  <select 
                    multiple 
                    value={track.genres} 
                    onChange={e => {
                      const selected = Array.from(e.target.selectedOptions, opt => opt.value);
                      updateTrack(track.id, 'genres', selected);
                    }} 
                    className="neon-select"
                  >
                    {AVAILABLE_GENRES.map(g => (
                      <option key={g} value={g}>{g}</option>
                    ))}
                  </select>
                  <small>Удерживайте Ctrl (или Cmd) для выбора нескольких жанров</small>
                </div>

                {/* Текст песни */}
                <div className="form-group">
                  <label>Текст песни (опционально)</label>
                  <textarea 
                    rows="3" 
                    value={track.lyrics} 
                    onChange={e => updateTrack(track.id, 'lyrics', e.target.value)} 
                    className="neon-textarea" 
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button type="submit" className="neon-btn">Опубликовать релиз</button>
            <button type="button" onClick={() => navigate(-1)} className="cancel-btn">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateRelease;