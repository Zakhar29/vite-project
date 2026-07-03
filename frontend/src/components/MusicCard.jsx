import { Link } from "react-router-dom";
import { useState } from "react";
import "../styles/musicCard.css";

function MusicCard({ item, onPlay, onAuthorClick }) {
  const [expanded, setExpanded] = useState(false);
  
  const isTrack = item?.type === 'track';
  const isAlbum = item?.type === 'album';

  // Определяем ссылку в зависимости от типа
  const linkTo = isTrack ? `/track/${item.id}` : `/album/${item.id}`;

  // Получаем данные для отображения
  const title = item?.title || 'Без названия';
  const coverUrl = item?.cover_url || '/default-cover.jpg';
  const artistName = item?.author?.nickname || 'Неизвестный исполнитель';
  const artistId = item?.author?.id;

  // Тип контента (Album, EP, Single, Track)
  const contentType = isAlbum
    ? (item?.subtype || item?.type_label || "Album")
    : "Track";

  const typeLabel = typeof contentType === "string"
    ? contentType.charAt(0).toUpperCase() + contentType.slice(1)
    : "Track";

  const year = item?.published_at_formatted
    || (item?.published_at ? new Date(item.published_at).getFullYear() : "2024");

  // Треки для альбома
  const tracks = item?.tracks || [];
  const visibleTracks = expanded ? tracks : tracks.slice(0, 3);

  const handlePlay = (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!onPlay) return;

    if (isTrack && item.track_url) {
      const track = {
        track_id: item.id,
        title: item.title,
        track_url: item.track_url,
        cover_url: item.cover_url,
        author_id: item.author?.id,
        author_nickname: item.author?.nickname,
        bpm: item.bpm
      };
      onPlay([track]);
    } else if (isAlbum && tracks.length > 0) {
      // Форматируем треки для плеера
      const formattedTracks = tracks.map(track => ({
        track_id: track.track_id || track.id,
        title: track.title,
        track_url: track.track_url,
        cover_url: item.cover_url,
        author_id: item.author?.id,
        author_nickname: item.author?.nickname,
        bpm: track.bpm,
        duration: track.duration
      }));
      onPlay(formattedTracks);
    }
  };

  const handleTrackPlay = (e, track, index) => {
    e.preventDefault();
    e.stopPropagation();

    if (!onPlay) return;

    const formattedTracks = tracks.map(t => ({
      track_id: t.track_id || t.id,
      title: t.title,
      track_url: t.track_url,
      cover_url: item.cover_url,
      author_id: item.author?.id,
      author_nickname: item.author?.nickname,
      bpm: t.bpm,
      duration: t.duration
    }));

    const currentTrack = {
      track_id: track.track_id || track.id,
      title: track.title,
      track_url: track.track_url,
      cover_url: item.cover_url,
      author_id: item.author?.id,
      author_nickname: item.author?.nickname,
      bpm: track.bpm,
      duration: track.duration
    };

    // Сохраняем в localStorage для плеера
    localStorage.setItem("playlist", JSON.stringify(formattedTracks));
    localStorage.setItem("currentTrack", JSON.stringify(currentTrack));
    localStorage.setItem("currentIndex", String(index));
    
    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));

    onPlay(formattedTracks);
  };

  const handleAuthorClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (artistId && onAuthorClick) {
      onAuthorClick(artistId);
    }
  };

  const handleImageError = (e) => {
    e.target.src = '/default-cover.jpg';
  };

  const handleToggleTracks = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setExpanded(!expanded);
  };

  return (
    <Link to={linkTo} className="music-card-link">
      <div className="music-card">
        <div className="music-card-image-wrapper">
          <img
            src={coverUrl}
            alt={title}
            className="music-card__image"
            loading="lazy"
            onError={handleImageError}
          />
          {/* ===== КНОПКА ВОСПРОИЗВЕДЕНИЯ ТОЛЬКО ДЛЯ ТРЕКОВ ===== */}
          {isTrack && item.track_url && (
            <button 
              className="music-card-play-btn"
              onClick={handlePlay}
              aria-label="Воспроизвести трек"
            >
              ▶
            </button>
          )}
          {/* ===== ДЛЯ АЛЬБОМОВ КНОПКИ НЕТ ===== */}
        </div>

        <div className="music-card__info">
          <h3>{title}</h3>
          <p className="artist" onClick={handleAuthorClick}>
            {artistName}
          </p>

          <div className="meta">
            <span className="badge">{typeLabel}</span>
            <span className="year">{year}</span>
          </div>

          {/* Дополнительная информация для рекомендаций */}
          {item?.similarity_score && (
            <div className="similarity-score">
              {Math.round(item.similarity_score * 100)}% совпадение
            </div>
          )}

          {item?.reason && (
            <div className="recommendation-reason">{item.reason}</div>
          )}

          {/* Список треков для альбома */}
          {isAlbum && tracks.length > 0 && (
            <>
              <button 
                className="music-card-toggle"
                onClick={handleToggleTracks}
              >
                {expanded ? 'Скрыть треки' : `Показать треки (${tracks.length})`}
              </button>
              
              {expanded && (
                <ul className="music-card-tracks">
                  {visibleTracks.map((track, idx) => (
                    <li 
                      key={track.track_id || track.id || idx}
                      className="music-card-track"
                      onClick={(e) => handleTrackPlay(e, track, idx)}
                    >
                      <span className="track-number">{idx + 1}.</span>
                      <span className="track-title">{track.title}</span>
                      {track.duration && (
                        <span className="track-duration">{track.duration}</span>
                      )}
                    </li>
                  ))}
                  {tracks.length > 3 && !expanded && (
                    <li className="music-card-track-more">
                      + еще {tracks.length - 3} треков
                    </li>
                  )}
                </ul>
              )}
            </>
          )}
        </div>
      </div>
    </Link>
  );
}

export default MusicCard;