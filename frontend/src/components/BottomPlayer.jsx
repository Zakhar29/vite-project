// components/BottomPlayer.jsx
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/bottomPlayer.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function IconShuffle({ active }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5"
        opacity={active ? 1 : 0.9}
      />
    </svg>
  );
}

function IconPrevious() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
      <path fill="currentColor" d="M6 6h2v12H6zm3.5 6 8.5 6V6z" />
    </svg>
  );
}

function IconNext() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
      <path fill="currentColor" d="M16 18h2V6h-2zm-11-6 8.5-6v12z" />
    </svg>
  );
}

function IconPlay() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <path fill="currentColor" d="M8 5v14l11-7z" />
    </svg>
  );
}

function IconPause() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <path fill="currentColor" d="M6 5h4v14H6zm8 0h4v14h-4z" />
    </svg>
  );
}

function IconRepeat({ active }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M17 1l4 4-4 4M3 11V9a4 4 0 0 1 4-4h14M7 23l-4-4 4-4M21 13v2a4 4 0 0 1-4 4H3"
        opacity={active ? 1 : 0.9}
      />
    </svg>
  );
}

function IconHeart({ filled }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.8"
        d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5.5-7 10-7 10z"
      />
    </svg>
  );
}

function IconVolume({ level }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        d="M11 5 6 9H3v6h3l5 4V5z"
      />
      {level > 0.05 && (
        <path
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          d="M15.5 8.5a5 5 0 0 1 0 7"
        />
      )}
      {level > 0.45 && (
        <path
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          d="M18 6a8 8 0 0 1 0 12"
        />
      )}
    </svg>
  );
}

function BottomPlayer() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isShuffled, setIsShuffled] = useState(false);
  const [isRepeated, setIsRepeated] = useState(false);
  const [playlist, setPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isLiked, setIsLiked] = useState(false);

  const audioRef = useRef(null);
  const hasTrack = currentTrack !== null;

  const loadFromStorage = () => {
    const savedTrack = localStorage.getItem("currentTrack");
    const savedPlaylist = localStorage.getItem("playlist");
    const savedIndex = localStorage.getItem("currentIndex");

    if (savedTrack) {
      setCurrentTrack(JSON.parse(savedTrack));
    }
    if (savedPlaylist) {
      setPlaylist(JSON.parse(savedPlaylist));
    }
    if (savedIndex) {
      setCurrentIndex(parseInt(savedIndex, 10));
    }
  };

  useEffect(() => {
    loadFromStorage();

    const handleTrackChange = () => {
      const savedTrack = localStorage.getItem("currentTrack");
      if (savedTrack) {
        const track = JSON.parse(savedTrack);
        setCurrentTrack(track);

        if (audioRef.current && track.track_url) {
          audioRef.current.src = track.track_url;
          audioRef.current.play()
            .then(() => setIsPlaying(true))
            .catch(() => setIsPlaying(false));
        }
      }
    };

    const handlePlaylistChange = () => {
      const savedPlaylist = localStorage.getItem("playlist");
      if (savedPlaylist) {
        setPlaylist(JSON.parse(savedPlaylist));
      }
    };

    window.addEventListener("trackChanged", handleTrackChange);
    window.addEventListener("playlistChanged", handlePlaylistChange);
    handleTrackChange();

    return () => {
      window.removeEventListener("trackChanged", handleTrackChange);
      window.removeEventListener("playlistChanged", handlePlaylistChange);
    };
  }, []);

  useEffect(() => {
    if (currentTrack) {
      localStorage.setItem("currentTrack", JSON.stringify(currentTrack));
    }
    if (playlist.length > 0) {
      localStorage.setItem("playlist", JSON.stringify(playlist));
    }
    localStorage.setItem("currentIndex", String(currentIndex));
  }, [currentTrack, playlist, currentIndex]);

  const playTrack = (track, index = 0, tracks = []) => {
    if (!track?.track_url) return;

    setCurrentTrack(track);
    setCurrentIndex(index);
    if (tracks.length > 0) setPlaylist(tracks);

    if (audioRef.current) {
      audioRef.current.src = track.track_url;
      audioRef.current.play()
        .then(() => {
          setIsPlaying(true);
          sendListening(track.track_id);
        })
        .catch(() => setIsPlaying(false));
    }
  };

  const sendListening = async (trackId) => {
    if (!trackId) return;
    try {
      await fetch(`${API_URL}/api/v1/social/track/${trackId}/listening`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
    } catch (err) {
      console.error("Ошибка отправки прослушивания:", err);
    }
  };

  const togglePlay = () => {
    if (!hasTrack || !audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play()
        .then(() => setIsPlaying(true))
        .catch((err) => console.error("Ошибка воспроизведения:", err));
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current && !isDragging) {
      const current = audioRef.current.currentTime;
      const total = audioRef.current.duration || 0;
      setCurrentTime(current);
      setProgress(total > 0 ? (current / total) * 100 : 0);
      if (currentTrack?.track_id) {
        window.dispatchEvent(new CustomEvent("playerProgress", {
          detail: {
            track_id: currentTrack.track_id,
            currentTime: current,
            duration: total,
            isPlaying: !audioRef.current.paused,
          },
        }));
      }
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    if (!hasTrack || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const seekTime = x * duration;
    if (audioRef.current) {
      audioRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
      setProgress(x * 100);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  useEffect(() => {
    const onSeek = (e) => {
      const percent = e.detail?.percent;
      if (audioRef.current && duration && typeof percent === "number") {
        audioRef.current.currentTime = percent * duration;
        setCurrentTime(percent * duration);
        setProgress(percent * 100);
      }
    };
    window.addEventListener("playerSeek", onSeek);
    return () => window.removeEventListener("playerSeek", onSeek);
  }, [duration]);

  const playNext = () => {
    if (playlist.length === 0 || !hasTrack) return;
    let nextIndex = currentIndex + 1;
    if (nextIndex >= playlist.length) {
      if (isRepeated) nextIndex = 0;
      else return;
    }
    const nextTrack = playlist[nextIndex];
    if (nextTrack) playTrack(nextTrack, nextIndex, playlist);
  };

  const playPrevious = () => {
    if (playlist.length === 0 || !hasTrack) return;
    let prevIndex = currentIndex - 1;
    if (prevIndex < 0) prevIndex = playlist.length - 1;
    const prevTrack = playlist[prevIndex];
    if (prevTrack) playTrack(prevTrack, prevIndex, playlist);
  };

  const handleEnded = () => {
    if (isRepeated && hasTrack && audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play();
    } else {
      playNext();
    }
  };

  const formatTime = (seconds) => {
    if (!seconds || Number.isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="bottom-player">
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />

      <div className="player-container">
        <div className="player-left">
          {hasTrack ? (
            <>
              <button
                type="button"
                className="player-cover-btn"
                onClick={() => navigate(`/track/${currentTrack.track_id}`)}
                aria-label="Открыть страницу трека"
              >
                <img
                  src={currentTrack.cover_url || "https://picsum.photos/56"}
                  alt=""
                  className="player-cover"
                />
              </button>

              <div className="player-track-meta">
                <button
                  type="button"
                  className="player-track-title"
                  onClick={() => navigate(`/track/${currentTrack.track_id}`)}
                >
                  {currentTrack.title || "Без названия"}
                </button>
                <button
                  type="button"
                  className="player-track-artist"
                  onClick={() => currentTrack.author_id && navigate(`/profile/${currentTrack.author_id}`)}
                >
                  {currentTrack.author_name || currentTrack.author_nickname || "Автор"}
                </button>
              </div>

              <button
                type="button"
                className={`player-like ${isLiked ? "is-active" : ""}`}
                onClick={() => setIsLiked(!isLiked)}
                aria-label="Нравится"
              >
                <IconHeart filled={isLiked} />
              </button>
            </>
          ) : (
            <>
              <div className="player-cover player-cover--placeholder" />
              <div className="player-track-meta">
                <span className="player-track-title player-track-title--muted">Ничего не играет</span>
                <span className="player-track-artist">Выберите трек</span>
              </div>
            </>
          )}
        </div>

        <div className="player-center">
          <div className="player-controls-buttons">
            <button
              type="button"
              className={`player-control ${isShuffled ? "is-active" : ""}`}
              onClick={() => setIsShuffled(!isShuffled)}
              disabled={!hasTrack}
              aria-label="Перемешать"
            >
              <IconShuffle active={isShuffled} />
            </button>

            <button
              type="button"
              className="player-control"
              onClick={playPrevious}
              disabled={!hasTrack}
              aria-label="Предыдущий трек"
            >
              <IconPrevious />
            </button>

            <button
              type="button"
              className="player-control player-control--play"
              onClick={togglePlay}
              disabled={!hasTrack}
              aria-label={isPlaying ? "Пауза" : "Воспроизвести"}
            >
              {isPlaying ? <IconPause /> : <IconPlay />}
            </button>

            <button
              type="button"
              className="player-control"
              onClick={playNext}
              disabled={!hasTrack}
              aria-label="Следующий трек"
            >
              <IconNext />
            </button>

            <button
              type="button"
              className={`player-control ${isRepeated ? "is-active" : ""}`}
              onClick={() => setIsRepeated(!isRepeated)}
              disabled={!hasTrack}
              aria-label="Повтор"
            >
              <IconRepeat active={isRepeated} />
            </button>
          </div>

          <div className="player-progress">
            <span className="player-time">{hasTrack ? formatTime(currentTime) : "0:00"}</span>
            <div
              className={`player-progress__bar ${!hasTrack ? "is-disabled" : ""}`}
              onClick={handleSeek}
              onMouseDown={() => setIsDragging(true)}
              onMouseUp={() => setIsDragging(false)}
              onMouseLeave={() => setIsDragging(false)}
              role="slider"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(progress)}
              aria-label="Прогресс воспроизведения"
            >
              <div className="player-progress__fill" style={{ width: `${hasTrack ? progress : 0}%` }} />
            </div>
            <span className="player-time">{hasTrack ? formatTime(duration) : "0:00"}</span>
          </div>
        </div>

        <div className="player-right">
          <span className="player-volume__icon" aria-hidden="true">
            <IconVolume level={volume} />
          </span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={handleVolumeChange}
            className="player-volume__slider"
            disabled={!hasTrack}
            aria-label="Громкость"
          />
        </div>
      </div>
    </div>
  );
}

export default BottomPlayer;
