import { useState } from "react";
import "../styles/profileTrack.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function formatDuration(value) {
  if (!value) return "0:00";
  if (typeof value === "string" && value.includes(":")) return value;

  const total = Math.floor(Number(value) || 0);
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function ProfileTrack({ track, onClick }) {
  const token = localStorage.getItem("access_token");
  const [isLiked, setIsLiked] = useState(track?.is_liked || false);
  const [isPlaying, setIsPlaying] = useState(false);

  if (!track) {
    return (
      <div className="profile-track-card profile-track-card--empty">
        <p>Трек не найден</p>
      </div>
    );
  }

  const trackId = track.track_id || track.id;
  const title = track.title || "Без названия";
  const coverUrl = track.cover_url || "/default-cover.jpg";
  const artistName = track.author?.nickname || track.author_nickname || "Неизвестный автор";
  const authorId = track.author?.id || track.author_id;
  const trackUrl = track.track_url || "";
  const duration = formatDuration(track.duration);

  const handlePlay = (e) => {
    e.stopPropagation();
    if (!trackUrl) {
      alert("У этого трека нет аудиофайла");
      return;
    }

    const trackData = {
      track_id: trackId,
      title,
      track_url: trackUrl,
      cover_url: coverUrl,
      author_id: authorId,
      author_nickname: artistName,
      bpm: track.bpm,
      duration: track.duration,
    };

    localStorage.setItem("currentTrack", JSON.stringify(trackData));
    window.dispatchEvent(new Event("trackChanged"));
    setIsPlaying(true);
  };

  const handleLike = async (e) => {
    e.stopPropagation();
    if (!token) {
      alert("Войдите, чтобы оценить трек");
      return;
    }

    try {
      const url = `${API_URL}/api/v1/social/track/${trackId}/${isLiked ? "unlike" : "like"}`;
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setIsLiked(!isLiked);
      }
    } catch (err) {
      console.error("Ошибка лайка:", err);
    }
  };

  const handleShare = (e) => {
    e.stopPropagation();
    const url = `${window.location.origin}/track/${trackId}`;
    if (navigator.share) {
      navigator.share({ title, url }).catch(() => {});
    } else {
      navigator.clipboard.writeText(url);
    }
  };

  return (
    <article className="profile-track-card" onClick={onClick}>
      <div className="profile-track-card__content">
        <div className="profile-track-card__left">
          <h3 className="profile-track-card__title">{title}</h3>
          <p className="profile-track-card__artist">{artistName}</p>

          <div className="profile-track-card__controls">
            <button
              type="button"
              className={`profile-track-card__btn profile-track-card__btn--play ${isPlaying ? "is-playing" : ""}`}
              onClick={handlePlay}
              aria-label="Воспроизвести"
            >
              ▶
            </button>
            <button
              type="button"
              className={`profile-track-card__btn ${isLiked ? "is-liked" : ""}`}
              onClick={handleLike}
              aria-label="Нравится"
            >
              {isLiked ? "♥" : "♡"}
            </button>
            <button
              type="button"
              className="profile-track-card__btn"
              onClick={handleShare}
              aria-label="Поделиться"
            >
              ↗
            </button>
          </div>

          <div className="profile-track-card__progress">
            <span>00:00</span>
            <div className="profile-track-card__progress-bar">
              <div className="profile-track-card__progress-fill" />
            </div>
            <span>{duration}</span>
          </div>
        </div>

        <div className="profile-track-card__cover">
          <img
            src={coverUrl}
            alt={title}
            loading="lazy"
            onError={(e) => {
              e.currentTarget.src = "/default-cover.jpg";
            }}
          />
        </div>
      </div>
    </article>
  );
}

export default ProfileTrack;
