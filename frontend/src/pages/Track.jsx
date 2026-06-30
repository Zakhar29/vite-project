import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Comment from "../components/Comment";
import CommentForm from "../components/CommentForm";
import "../styles/track.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Track() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [track, setTrack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLiked, setIsLiked] = useState(false);
  const [comments, setComments] = useState([]);
  const [similarTracks, setSimilarTracks] = useState([]);
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false);

  // ========== Загрузка данных ==========

  useEffect(() => {
    loadTrackData();
  }, [id]);

  const loadTrackData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Получаем информацию о треке
      const trackResponse = await fetch(`${API_URL}/api/v1/track-page/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!trackResponse.ok) {
        if (trackResponse.status === 404) {
          throw new Error("Трек не найден");
        }
        throw new Error("Ошибка загрузки трека");
      }

      const trackData = await trackResponse.json();
      setTrack(trackData.track);
      setIsLiked(false);

      // Загружаем комментарии
      await loadComments();

      // Загружаем похожие треки
      await loadSimilarTracks();

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadComments = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/track-page/${id}/comments?skip=0&limit=20`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (response.ok) {
        const data = await response.json();
        setComments(data.items || []);
      }
    } catch (err) {
      console.error("Ошибка загрузки комментариев:", err);
    }
  };

  // ========== Загрузка похожих треков ==========

  const loadSimilarTracks = async () => {
    setIsLoadingSimilar(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/music-feed/tracks/${id}/similar?limit=10`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (response.ok) {
        const data = await response.json();
        setSimilarTracks(data.items || []);
      }
    } catch (err) {
      console.error("Ошибка загрузки похожих треков:", err);
    } finally {
      setIsLoadingSimilar(false);
    }
  };

  // ========== Управление плеером ==========

  const playTrack = () => {
    if (!track) return;

    const trackData = {
      track_id: track.track_id,
      title: track.title,
      track_url: track.track_url,
      author_id: track.author?.id,
      author_name: track.author?.nickname,
      cover_url: track.cover_url || "https://picsum.photos/56",
    };

    // Формируем плейлист: текущий трек + похожие
    const playlist = [
      trackData,
      ...similarTracks.map(item => ({
        track_id: item.track_id,
        title: item.title,
        track_url: item.track_url,
        author_id: item.author?.id,
        author_name: item.author?.nickname,
        cover_url: item.cover_url,
      }))
    ];

    localStorage.setItem("currentTrack", JSON.stringify(trackData));
    localStorage.setItem("playlist", JSON.stringify(playlist));
    localStorage.setItem("currentIndex", "0");

    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  // ========== Воспроизведение похожего трека ==========

  const playSimilarTrack = (similarTrack, index) => {
    const trackData = {
      track_id: similarTrack.track_id,
      title: similarTrack.title,
      track_url: similarTrack.track_url,
      author_id: similarTrack.author?.id,
      author_name: similarTrack.author?.nickname,
      cover_url: similarTrack.cover_url,
    };

    // Плейлист: текущий трек + все похожие
    const currentTrackData = {
      track_id: track.track_id,
      title: track.title,
      track_url: track.track_url,
      author_id: track.author?.id,
      author_name: track.author?.nickname,
      cover_url: track.cover_url || "https://picsum.photos/56",
    };

    const playlist = [
      currentTrackData,
      ...similarTracks.map(item => ({
        track_id: item.track_id,
        title: item.title,
        track_url: item.track_url,
        author_id: item.author?.id,
        author_name: item.author?.nickname,
        cover_url: item.cover_url,
      }))
    ];

    localStorage.setItem("currentTrack", JSON.stringify(trackData));
    localStorage.setItem("playlist", JSON.stringify(playlist));
    localStorage.setItem("currentIndex", String(index + 1)); // +1 потому что первый — текущий трек

    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  // ========== Лайк ==========

  const handleLike = async () => {
    if (!token) {
      alert("Войдите, чтобы оценить трек");
      return;
    }

    const url = `${API_URL}/api/v1/social/track/${id}/${isLiked ? "unlike" : "like"}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setIsLiked(!isLiked);
        setTrack(prev => ({
          ...prev,
          liked_quantity: prev.liked_quantity + (isLiked ? -1 : 1),
        }));
      }
    } catch (err) {
      console.error("Ошибка лайка:", err);
    }
  };

  // ========== Обновление комментариев ==========

  const handleCommentAdded = () => {
    loadComments();
    setTrack(prev => ({
      ...prev,
      comments_quantity: (prev.comments_quantity || 0) + 1,
    }));
  };

  // ========== Состояние загрузки ==========

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Загрузка трека...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Ошибка</h2>
        <p>{error}</p>
        <button onClick={loadTrackData}>Попробовать снова</button>
      </div>
    );
  }

  if (!track) {
    return (
      <div className="not-found-container">
        <h2>Трек не найден</h2>
        <p>Возможно, он был удалён или ещё не опубликован</p>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="track-page">
      <div className="track-content">

        {/* ===== ЛЕВАЯ КОЛОНКА ===== */}
        <div className="left-column">

          {/* Карточка трека */}
          <div className="track-main-card">
            <div className="track-text">
              <h1>{track.title}</h1>
              <p
                className="artist-name"
                onClick={() => navigate(`/profile/${track.author?.id}`)}
                style={{ cursor: 'pointer' }}
              >
                {track.author?.nickname || "Неизвестный автор"}
              </p>

              <div className="controls">
                <button className="play-btn-large" onClick={playTrack}>
                  ▶
                </button>
                <button
                  className={`like-btn ${isLiked ? "active" : ""}`}
                  onClick={handleLike}
                >
                  {isLiked ? "❤️" : "♡"}
                </button>
                <button>↗</button>
                <button>⋯</button>
              </div>

              <div className="track-stats">
                <span>❤️ {track.liked_quantity || 0}</span>
                <span>💬 {track.comments_quantity || 0}</span>
                <span>🎧 {track.listening_quantity || 0}</span>
              </div>

              <div className="track-genres">
                {track.genres?.map((genre, idx) => (
                  <span key={idx} className="genre-tag">#{genre}</span>
                ))}
              </div>

              {track.track_text && (
                <div className="track-lyrics">
                  <h4>Текст</h4>
                  <p>{track.track_text}</p>
                </div>
              )}
            </div>

            <img
              src={track.cover_url || "https://picsum.photos/500/500?music"}
              alt={track.title}
              className="cover"
            />
          </div>

          {/* ===== КОММЕНТАРИИ ===== */}
          <CommentForm
            entityId={id}
            entityType="track"
            onCommentAdded={handleCommentAdded}
          />

          <div className="comments-list">
            {comments.length > 0 ? (
              comments.map((comment) => (
                <Comment
                  key={comment.id}
                  comment={comment}
                  onUpdate={loadComments}
                />
              ))
            ) : (
              <p className="no-comments">Пока нет комментариев. Будьте первым!</p>
            )}
          </div>

        </div>

        {/* ===== ПРАВАЯ КОЛОНКА ===== */}
        <div className="right-column">

          {/* Артист */}
          <div className="side-block">
            <h3>Артист</h3>
            <div className="artist-card">
              <img
                src={track.author?.avatar_url || "https://picsum.photos/80"}
                alt={track.author?.nickname}
                onClick={() => navigate(`/profile/${track.author?.id}`)}
                style={{ cursor: 'pointer' }}
              />
              <div>
                <p
                  onClick={() => navigate(`/profile/${track.author?.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  {track.author?.nickname || "Неизвестный автор"}
                </p>
                <button>Подписаться</button>
              </div>
            </div>
          </div>

          {/* Теги */}
          <div className="side-block">
            <h3>Теги</h3>
            <div className="tags">
              {track.genres?.map((genre, idx) => (
                <span key={idx}>#{genre}</span>
              ))}
            </div>
          </div>

          {/* ===== ПОХОЖИЕ ТРЕКИ ===== */}
          <div className="side-block">
            <h3>Похожие треки</h3>
            {isLoadingSimilar ? (
              <div className="loading-mini">Загрузка...</div>
            ) : similarTracks.length > 0 ? (
              similarTracks.map((item, index) => (
                <div
                  key={item.track_id || index}
                  className="mini-track"
                  onClick={() => playSimilarTrack(item, index)}
                  style={{ cursor: 'pointer' }}
                >
                  <img
                    src={item.cover_url || "https://picsum.photos/70"}
                    alt={item.title}
                  />
                  <div>
                    <p>{item.title}</p>
                    <span>{item.author?.nickname || "Автор"}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-similar">Нет похожих треков</p>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}

export default Track;