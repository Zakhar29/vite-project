import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/album.css";
import "../styles/track.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Album() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [album, setAlbum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLiked, setIsLiked] = useState(false);
  const [isFollowed, setIsFollowed] = useState(false);

  // ========== Загрузка данных ==========

  useEffect(() => {
    loadAlbumData();
  }, [id]);

  const loadAlbumData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/album/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Альбом не найден");
        }
        throw new Error("Ошибка загрузки альбома");
      }

      const data = await response.json();
      setAlbum(data.album);

      setIsLiked(false);
      setIsFollowed(false);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ========== Управление плеером ==========


  const playAlbum = () => {
    if (!album?.tracks?.length) {
      alert("В альбоме нет треков");
      return;
    }

    const tracks = album.tracks.map(track => ({
      ...track,
      author_name: album.author?.nickname || "Неизвестный автор",
      author_id: album.author?.id,
      cover_url: album.cover_url,
    }));

    const firstTrack = tracks[0];
    if (firstTrack?.track_url) {
      // Сохраняем в localStorage
      localStorage.setItem("currentTrack", JSON.stringify(firstTrack));
      localStorage.setItem("playlist", JSON.stringify(tracks));
      localStorage.setItem("currentIndex", "0");

      console.log("🎵 Сохранён трек в localStorage:", firstTrack);

      // Диспатчим события
      window.dispatchEvent(new Event("trackChanged"));
      window.dispatchEvent(new Event("playlistChanged"));

      console.log("📤 События отправлены");
    } else {
      alert("У трека нет аудиофайла");
    }
  };

  const playTrack = (track, index) => {
    if (!track?.track_url) {
      alert("У трека нет аудиофайла");
      return;
    }

    const tracks = album.tracks.map(t => ({
      ...t,
      author_name: album.author?.nickname || "Неизвестный автор",
      author_id: album.author?.id,
      cover_url: album.cover_url,
    }));

    const trackWithMeta = {
      ...track,
      author_name: album.author?.nickname || "Неизвестный автор",
      author_id: album.author?.id,
      cover_url: album.cover_url,
    };

    console.log("🎵 Сохранён трек в localStorage:", trackWithMeta);

    localStorage.setItem("currentTrack", JSON.stringify(trackWithMeta));
    localStorage.setItem("playlist", JSON.stringify(tracks));
    localStorage.setItem("currentIndex", String(index));

    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));

    console.log("📤 События отправлены");
  };

  // ========== Обработчики ==========

  const handleLike = async () => {
    if (!token) {
      alert("Войдите, чтобы оценить альбом");
      return;
    }

    const url = `${API_URL}/api/v1/social/album/${id}/${isLiked ? "unlike" : "like"}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setIsLiked(!isLiked);
        setAlbum(prev => ({
          ...prev,
          liked_quantity: prev.liked_quantity + (isLiked ? -1 : 1),
        }));
      }
    } catch (err) {
      console.error("Ошибка лайка:", err);
    }
  };

  const handleFollow = async () => {
    if (!token) {
      alert("Войдите, чтобы подписаться");
      return;
    }

    const url = `${API_URL}/api/v1/social/album/${id}/${isFollowed ? "unfollow" : "follow"}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setIsFollowed(!isFollowed);
        setAlbum(prev => ({
          ...prev,
          follower_quantity: prev.follower_quantity + (isFollowed ? -1 : 1),
        }));
      }
    } catch (err) {
      console.error("Ошибка подписки:", err);
    }
  };

  // ========== Состояние загрузки ==========

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка альбома...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Ошибка</h2>
        <p>{error}</p>
        <button onClick={loadAlbumData}>Попробовать снова</button>
      </div>
    );
  }

  if (!album) {
    return (
      <div className="not-found-container">
        <h2>Альбом не найден</h2>
        <p>Возможно, он был удалён или ещё не опубликован</p>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="album-page">

      {/* ===== ЗАГОЛОВОК АЛЬБОМА ===== */}
      <div className="album-header">

        <img
          src={album.cover_url || "https://picsum.photos/300"}
          className="album-cover"
          alt={album.title}
        />

        <div className="album-info">
          <h1>{album.title}</h1>
          <p
            className="album-artist"
            onClick={() => navigate(`/profile/${album.author?.id}`)}
            style={{ cursor: 'pointer' }}
          >
            {album.author?.nickname || "Неизвестный автор"}
          </p>

          {album.description && (
            <p className="album-desc">{album.description}</p>
          )}

          <div className="album-meta">
            <span>{album.tracks_count || 0} треков</span>
            <span className="separator">•</span>
            <span>❤️ {album.liked_quantity || 0}</span>
            <span className="separator">•</span>
            <span>👤 {album.follower_quantity || 0} подписчиков</span>
            <span className="separator">•</span>
            <span>🎧 {album.listening_quantity || 0} прослушиваний</span>
          </div>

          <div className="album-buttons">
            <button
              className="play-btn"
              onClick={playAlbum}
              disabled={!album.tracks?.length}
            >
              ▶ Воспроизвести
            </button>
            <button className="shuffle-btn">🔀 Перемешать</button>
            <button
              className={`like-btn ${isLiked ? "active" : ""}`}
              onClick={handleLike}
            >
              {isLiked ? "❤️" : "🤍"} {album.liked_quantity || 0}
            </button>
            <button
              className={`follow-btn ${isFollowed ? "active" : ""}`}
              onClick={handleFollow}
            >
              {isFollowed ? "✅ Подписан" : "➕ Подписаться"}
            </button>
          </div>
        </div>

      </div>

      {/* ===== СПИСОК ТРЕКОВ ===== */}
      <div className="tracks">

        <h2>Треки</h2>

        <table className="tracks-table">

          <thead>
            <tr>
              <th>#</th>
              <th>Название</th>
              <th>Исполнитель</th>
              <th>Альбом</th>
              <th>Прослушивания</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {album.tracks && album.tracks.length > 0 ? (
              album.tracks.map((track, index) => (
                <tr
                  key={track.track_id || index}
                  className="track-row"
                >
                  <td>{index + 1}</td>
                  <td
                    className="track-name"
                    onClick={() => navigate(`/track/${track.track_id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    {track.title}
                  </td>
                  <td>{album.author?.nickname || "Неизвестен"}</td>
                  <td>{album.title}</td>
                  <td>🎧 {track.listening_quantity || 0}</td>
                  <td>
                    <button
                      className="track-play-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        playTrack(track, index);
                      }}
                      title="Воспроизвести трек"
                    >
                      ▶
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="empty-tracks">
                  В альбоме пока нет треков
                </td>
              </tr>
            )}
          </tbody>

        </table>

      </div>

    </div>
  );
}

export default Album;