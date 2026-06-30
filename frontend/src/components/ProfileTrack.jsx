// components/ProfileTrack.jsx
import { useState } from "react";
import "../styles/profileTrack.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function ProfileTrack({ track, onClick }) {
  const token = localStorage.getItem("access_token");
  const [isLiked, setIsLiked] = useState(track?.is_liked || false);
  const [likesCount, setLikesCount] = useState(track?.liked_quantity || 0);
  const [isPlaying, setIsPlaying] = useState(false);

  // ========== Если track не передан ==========
  if (!track) {
    return (
      <div className="profile-track neon-track">
        <p className="track-empty">Трек не найден</p>
      </div>
    );
  }

  // ========== Безопасное получение данных ==========
  const trackId = track.track_id || track.id;
  const title = track.title || 'Без названия';
  const coverUrl = track.cover_url || '/default-cover.jpg';
  
  // ===== ИСПРАВЛЕНО: правильное получение имени автора =====
  const artistName = track.author?.nickname || track.author_nickname || 'Неизвестный автор';
  const authorId = track.author?.id || track.author_id;
  
  const bpm = track.bpm || 0;
  const listeningQuantity = track.listening_quantity || 0;
  const commentsQuantity = track.comments_quantity || 0;
  const trackUrl = track.track_url || '';
  const year = track.published_at_formatted;

  // ========== Обработчик воспроизведения ==========
  const handlePlay = (e) => {
    e.stopPropagation();
    if (!trackUrl) {
      alert('У этого трека нет аудиофайла');
      return;
    }

    const trackData = {
      track_id: trackId,
      title: title,
      track_url: trackUrl,
      cover_url: coverUrl,
      author_id: authorId,
      author_nickname: artistName,
      bpm: bpm,
      duration: track.duration
    };

    localStorage.setItem("currentTrack", JSON.stringify(trackData));
    window.dispatchEvent(new Event("trackChanged"));
    setIsPlaying(true);
  };

  // ========== Обработчик лайка ==========
  const handleLike = async (e) => {
    e.stopPropagation();
    if (!token) {
      alert('Войдите, чтобы оценить трек');
      return;
    }

    try {
      const url = `${API_URL}/api/v1/social/track/${trackId}/${isLiked ? 'unlike' : 'like'}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setIsLiked(!isLiked);
        setLikesCount(prev => isLiked ? prev - 1 : prev + 1);
      }
    } catch (err) {
      console.error('Ошибка лайка:', err);
    }
  };

  // ========== Обработчик клика ==========
  const handleClick = () => {
    if (onClick) {
      onClick();
    }
  };

  // ========== Рендер ==========

  return (
    <div className="profile-track" onClick={handleClick}>
      <div className="track-left">
        <img
          src={coverUrl}
          alt={title}
          className="track-cover"
          onError={(e) => e.target.src = '/default-cover.jpg'}
        />
        <div className="track-info">
          <h3 className="track-title">{title}</h3>
          <span className="track-artist">{artistName}</span>
        </div>
      </div>

      <div className="track-center">
        {bpm > 0 && (
          <span className="track-bpm">{bpm} BPM</span>
        )}
        <span className="track-year">{year}</span>
      </div>

      <div className="track-right">
        <div className="track-stats">
          <span className="stat-item">🎧 {listeningQuantity}</span>
          <span className="stat-item">💬 {commentsQuantity}</span>
        </div>
        <div className="track-controls">
          <button 
            className="control-btn play-btn" 
            onClick={handlePlay}
            title="Воспроизвести"
          >
            ▶
          </button>
          <button 
            className={`control-btn like-btn ${isLiked ? 'liked' : ''}`}
            onClick={handleLike}
            title={isLiked ? 'Убрать лайк' : 'Лайк'}
          >
            {isLiked ? '❤️' : '♡'} {likesCount}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProfileTrack;