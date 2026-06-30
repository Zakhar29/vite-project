// components/AlbumCard.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "../styles/albumCard.css";

function AlbumCard({ album, onClick, onPlay }) {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);

  if (!album) return null;

  // ========== Безопасное получение данных ==========
  const albumId = album.id || album.album_id;
  const title = album.title || 'Без названия';
  const coverUrl = album.cover_url || album.cover || '/default-cover.jpg';
  
  const artistName = album.author?.nickname || 'Неизвестный исполнитель';
  const artistId = album.author?.id;
  
  const albumType = album.subtype || album.type || 'Альбом';
  const year = album.published_at_formatted || '2024';
  const likes = album.liked_quantity || 0;
  const followers = album.follower_quantity || 0;
  const listening = album.listening_quantity || 0;
  const tracksCount = album.tracks_count || album.tracks?.length || 0;

  const tracks = album.tracks || album.tracks_preview || [];
  const visibleTracks = expanded ? tracks : tracks.slice(0, 3);

  // ========== Функции из страницы альбома ==========

  const playAlbum = () => {
    if (!tracks?.length) {
      alert("В альбоме нет треков");
      return;
    }

    const formattedTracks = tracks.map(track => ({
      ...track,
      author_name: artistName,
      author_id: artistId,
      cover_url: coverUrl,
    }));

    const firstTrack = formattedTracks[0];
    if (firstTrack?.track_url) {
      localStorage.setItem("currentTrack", JSON.stringify(firstTrack));
      localStorage.setItem("playlist", JSON.stringify(formattedTracks));
      localStorage.setItem("currentIndex", "0");

      console.log("🎵 Сохранён трек в localStorage:", firstTrack);

      window.dispatchEvent(new Event("trackChanged"));
      window.dispatchEvent(new Event("playlistChanged"));

      console.log("📤 События отправлены");
      
      if (onPlay) {
        onPlay(formattedTracks);
      }
    } else {
      alert("У трека нет аудиофайла");
    }
  };

  const playTrack = (track, index) => {
    if (!track?.track_url) {
      alert("У трека нет аудиофайла");
      return;
    }

    const formattedTracks = tracks.map(t => ({
      ...t,
      author_name: artistName,
      author_id: artistId,
      cover_url: coverUrl,
    }));

    const trackWithMeta = {
      ...track,
      author_name: artistName,
      author_id: artistId,
      cover_url: coverUrl,
    };

    console.log("🎵 Сохранён трек в localStorage:", trackWithMeta);

    localStorage.setItem("currentTrack", JSON.stringify(trackWithMeta));
    localStorage.setItem("playlist", JSON.stringify(formattedTracks));
    localStorage.setItem("currentIndex", String(index));

    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));

    console.log("📤 События отправлены");
    
    if (onPlay) {
      onPlay(formattedTracks);
    }
  };

  // ========== Обработчики ==========

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (albumId) {
      navigate(`/album/${albumId}`);
    }
  };

  const handleToggleTracks = (e) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  const handleAuthorClick = (e) => {
    e.stopPropagation();
    if (artistId) {
      navigate(`/profile/${artistId}`);
    }
  };

  // ========== Рендер ==========

  return (
    <div className="album-card" onClick={handleClick}>
      <div className="album-card-image-wrapper">
        <img
          src={coverUrl}
          alt={title}
          className="album-card-image"
          loading="lazy"
          onError={(e) => e.target.src = '/default-cover.jpg'}
        />
        <button 
          className="album-card-play-btn"
          onClick={(e) => {
            e.stopPropagation();
            playAlbum();
          }}
          aria-label="Воспроизвести альбом"
        >
          ▶
        </button>
        <span className="album-card-badge">{albumType}</span>
      </div>

      <div className="album-card-info">
        <h4 className="album-card-title" title={title}>{title}</h4>
        <p 
          className="album-card-artist" 
          onClick={handleAuthorClick}
        >
          {artistName}
        </p>

        <div className="album-card-meta">
          <span>{tracksCount} треков</span>
          <span>•</span>
          <span>❤️ {likes}</span>
          {followers > 0 && (
            <>
              <span>•</span>
              <span>👤 {followers}</span>
            </>
          )}
          {listening > 0 && (
            <>
              <span>•</span>
              <span>🎧 {listening}</span>
            </>
          )}
          <span className="album-card-year">{year}</span>
        </div>

        {tracks.length > 0 && (
          <>
            <button 
              className="album-card-toggle"
              onClick={handleToggleTracks}
            >
              {expanded ? 'Скрыть треки' : `Показать треки (${tracks.length})`}
            </button>

            {expanded && (
              <ul className="album-card-tracks">
                {visibleTracks.map((track, idx) => (
                  <li 
                    key={track.track_id || track.id || idx}
                    className="album-card-track"
                    onClick={(e) => {
                      e.stopPropagation();
                      playTrack(track, idx);
                    }}
                  >
                    <span className="track-number">{idx + 1}.</span>
                    <span className="track-title">{track.title}</span>
                    {track.duration && (
                      <span className="track-duration">{track.duration}</span>
                    )}
                  </li>
                ))}
                {tracks.length > 3 && !expanded && (
                  <li className="album-card-track-more">
                    + еще {tracks.length - 3} треков
                  </li>
                )}
              </ul>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default AlbumCard;