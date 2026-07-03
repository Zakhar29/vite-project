import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Comment from "../components/Comment";
import CommentForm from "../components/CommentForm";
import Avatar from "../components/Avatar";
import "../styles/track.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

const MOCK_PLAYLISTS = [
  { id: 1, title: "Cyberpunk Essentials", tracks: 18, cover: "https://picsum.photos/seed/cyberpunk/120" },
  { id: 2, title: "Late Night Drives", tracks: 12, cover: "https://picsum.photos/seed/latenight/120" },
];

function formatTime(seconds) {
  if (!seconds || Number.isNaN(seconds)) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function formatCount(num) {
  if (!num) return "0";
  return Number(num).toLocaleString("ru-RU");
}

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
  const [currentUser, setCurrentUser] = useState(null);
  const [playback, setPlayback] = useState({ current: 0, duration: 0, isActive: false, isPlaying: false });

  useEffect(() => {
    loadTrackData();
  }, [id]);

  useEffect(() => {
    const onProgress = (e) => {
      const detail = e.detail || {};
      if (String(detail.track_id) === String(id)) {
        setPlayback({
          current: detail.currentTime || 0,
          duration: detail.duration || 0,
          isActive: true,
          isPlaying: detail.isPlaying,
        });
      } else {
        setPlayback((prev) => ({ ...prev, isActive: false }));
      }
    };
    window.addEventListener("playerProgress", onProgress);
    return () => window.removeEventListener("playerProgress", onProgress);
  }, [id]);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => data && setCurrentUser(data))
      .catch(() => {});
  }, [token]);

  const loadTrackData = async () => {
    setLoading(true);
    setError(null);

    try {
      const trackResponse = await fetch(`${API_URL}/api/v1/track-page/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!trackResponse.ok) {
        throw new Error(trackResponse.status === 404 ? "Трек не найден" : "Ошибка загрузки трека");
      }

      const trackData = await trackResponse.json();
      setTrack(trackData.track);
      setIsLiked(false);
      await loadComments();
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
      console.error(err);
    }
  };

  const loadSimilarTracks = async () => {
    setIsLoadingSimilar(true);
    try {
      const response = await fetch(`${API_URL}/api/v1/music-feed/tracks/${id}/similar?limit=5`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        setSimilarTracks(data.items || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingSimilar(false);
    }
  };

  const buildTrackPayload = (item) => ({
    track_id: item.track_id || item.id,
    title: item.title,
    track_url: item.track_url,
    author_id: item.author?.id || item.author_id,
    author_name: item.author?.nickname,
    author_nickname: item.author?.nickname,
    cover_url: item.cover_url,
  });

  const playTrack = (targetTrack = track, playlistItems = similarTracks) => {
    if (!targetTrack?.track_url) {
      alert("У трека нет аудиофайла");
      return;
    }

    const current = buildTrackPayload(targetTrack);
    const playlist = [
      current,
      ...playlistItems.map(buildTrackPayload).filter((t) => t.track_url),
    ];

    localStorage.setItem("currentTrack", JSON.stringify(current));
    localStorage.setItem("playlist", JSON.stringify(playlist));
    localStorage.setItem("currentIndex", "0");
    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  const playSimilarTrack = (item, index) => {
    const current = buildTrackPayload(track);
    const playlist = [current, ...similarTracks.map(buildTrackPayload)];
    const target = buildTrackPayload(item);

    localStorage.setItem("currentTrack", JSON.stringify(target));
    localStorage.setItem("playlist", JSON.stringify(playlist));
    localStorage.setItem("currentIndex", String(index + 1));
    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  const handleSeek = (e) => {
    const value = Number(e.target.value);
    window.dispatchEvent(new CustomEvent("playerSeek", { detail: { percent: value / 100 } }));
    setPlayback((prev) => ({
      ...prev,
      current: (value / 100) * (prev.duration || 0),
    }));
  };

  const handleLike = async () => {
    if (!token) {
      navigate("/login");
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
        setTrack((prev) => ({
          ...prev,
          liked_quantity: (prev.liked_quantity || 0) + (isLiked ? -1 : 1),
        }));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFollow = async () => {
    if (!token) {
      navigate("/login");
      return;
    }
    try {
      await fetch(`${API_URL}/api/v1/user/${track.author.id}/follow`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleShare = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) {
        await navigator.share({ title: track.title, url });
      } else {
        await navigator.clipboard.writeText(url);
        alert("Ссылка скопирована");
      }
    } catch {
      /* cancelled */
    }
  };

  const handleDownload = () => {
    if (track?.track_url) {
      window.open(track.track_url, "_blank");
    }
  };

  if (loading) {
    return (
      <div className="track-page">
        <div className="track-page__loading">Загрузка трека...</div>
      </div>
    );
  }

  if (error || !track) {
    return (
      <div className="track-page">
        <div className="track-page__error">
          <p>{error || "Трек не найден"}</p>
          <button type="button" onClick={loadTrackData}>Попробовать снова</button>
        </div>
      </div>
    );
  }

  const progressPercent = playback.duration
    ? (playback.current / playback.duration) * 100
    : 0;

  const genres = track.genres?.length ? track.genres : ["Electronic"];

  return (
    <div className="track-page">
      <div className="track-page__inner">
        <div className="track-main">
          <section className="track-hero">
            <div className="track-hero__info">
              <h1>{track.title}</h1>
              <p
                className="track-hero__artist"
                onClick={() => navigate(`/profile/${track.author?.id}`)}
              >
                {track.author?.nickname || "Неизвестный автор"}
              </p>

              <div className="track-hero__controls">
                <button type="button" className="track-hero__btn track-hero__btn--play" onClick={() => playTrack()}>
                  ▶
                </button>
                <button
                  type="button"
                  className={`track-hero__btn ${isLiked ? "active" : ""}`}
                  onClick={handleLike}
                >
                  ♥
                </button>
                <button type="button" className="track-hero__btn" onClick={handleShare}>↗</button>
                <button type="button" className="track-hero__btn">⋯</button>
                <button type="button" className="track-hero__btn" onClick={handleDownload}>↓</button>
              </div>

              <div className="track-hero__progress">
                <span>{formatTime(playback.isActive ? playback.current : 0)}</span>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={playback.isActive ? progressPercent : 0}
                  onChange={handleSeek}
                />
                <span>{formatTime(playback.duration || 0)}</span>
              </div>
            </div>

            <img
              src={track.cover_url || "https://picsum.photos/500/500?music"}
              alt={track.title}
              className="track-hero__cover"
            />
          </section>

          <CommentForm
            entityId={id}
            entityType="track"
            userAvatar={currentUser?.avatar_url}
            onCommentAdded={() => {
              loadComments();
              setTrack((prev) => ({
                ...prev,
                comments_quantity: (prev.comments_quantity || 0) + 1,
              }));
            }}
          />

          <h3 className="track-comments__title">Комментарии</h3>
          {comments.length > 0 ? (
            comments.map((comment) => (
              <Comment
                key={comment.id}
                comment={comment}
                entityType="track"
                entityId={id}
                userAvatar={currentUser?.avatar_url}
                onUpdate={loadComments}
              />
            ))
          ) : (
            <p className="track-comments__empty">Пока нет комментариев. Будьте первым!</p>
          )}
        </div>

        <aside className="track-sidebar">
          <div className="track-side-block">
            <h3>Артист</h3>
            <div className="track-artist-card">
              <Avatar
                src={track.author?.avatar_url}
                alt={track.author?.nickname}
                className="track-artist-card__avatar"
                onClick={() => navigate(`/profile/${track.author?.id}`)}
              />
              <div>
                <p
                  className="track-artist-card__name"
                  onClick={() => navigate(`/profile/${track.author?.id}`)}
                >
                  {track.author?.nickname || "Автор"}
                </p>
                <button type="button" onClick={handleFollow}>Подписаться</button>
              </div>
            </div>
          </div>

          <div className="track-side-block">
            <h3>Теги</h3>
            <div className="track-tags">
              {genres.map((genre) => (
                <span key={genre}>#{genre}</span>
              ))}
            </div>
          </div>

          <div className="track-side-block">
            <div className="track-side-block__header">
              <h3>Похожие треки</h3>
              <a href="/search" className="track-side-block__link">View all &gt;</a>
            </div>
            {isLoadingSimilar ? (
              <p className="track-comments__empty">Загрузка...</p>
            ) : similarTracks.length > 0 ? (
              similarTracks.slice(0, 3).map((item, index) => (
                <div
                  key={item.track_id || index}
                  className="track-mini-item"
                  onClick={() => playSimilarTrack(item, index)}
                >
                  <img src={item.cover_url || "https://picsum.photos/70"} alt={item.title} />
                  <div>
                    <p className="track-mini-item__title">{item.title}</p>
                    <p className="track-mini-item__artist">{item.author?.nickname || "Автор"}</p>
                    <p className="track-mini-item__stats">
                      {formatCount(item.listening_quantity)} · {formatCount(item.liked_quantity)} лайков
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="track-comments__empty">Нет похожих треков</p>
            )}
          </div>

          <div className="track-side-block">
            <div className="track-side-block__header">
              <h3>В плейлистах</h3>
              <span className="track-side-block__link">Посмотреть всё &gt;</span>
            </div>
            {MOCK_PLAYLISTS.map((playlist) => (
              <div key={playlist.id} className="track-playlist-item">
                <img src={playlist.cover} alt={playlist.title} />
                <div>
                  <p className="track-playlist-item__title">{playlist.title}</p>
                  <p className="track-playlist-item__count">{playlist.tracks} треков</p>
                </div>
              </div>
            ))}
          </div>

          <div className="track-side-block">
            <h3>LIKED BY</h3>
            <div className="track-liked-by">
              <img src="https://i.pravatar.cc/80?img=12" alt="" />
              <img src="https://i.pravatar.cc/80?img=32" alt="" />
              <img src="https://i.pravatar.cc/80?img=45" alt="" />
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default Track;
