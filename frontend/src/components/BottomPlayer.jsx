// components/BottomPlayer.jsx
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/bottomPlayer.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function BottomPlayer() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [currentTrack, setCurrentTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isShuffled, setIsShuffled] = useState(false);
  const [isRepeated, setIsRepeated] = useState(false);
  const [playlist, setPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const audioRef = useRef(null);
  const hasTrack = currentTrack !== null;

  // ========== Загрузка из localStorage ==========

  const loadFromStorage = () => {
    const savedTrack = localStorage.getItem("currentTrack");
    const savedPlaylist = localStorage.getItem("playlist");
    const savedIndex = localStorage.getItem("currentIndex");

    if (savedTrack) {
      const track = JSON.parse(savedTrack);
      console.log("🎵 Загружен трек из localStorage:", track.title);
      setCurrentTrack(track);
    }
    if (savedPlaylist) {
      setPlaylist(JSON.parse(savedPlaylist));
    }
    if (savedIndex) {
      setCurrentIndex(parseInt(savedIndex));
    }
    setIsLoaded(true);
  };

  // ========== Монтирование + слушатели событий ==========

  useEffect(() => {
    loadFromStorage();

    const handleTrackChange = () => {
      console.log("🔔 Событие trackChanged получено");
      const savedTrack = localStorage.getItem("currentTrack");
      if (savedTrack) {
        const track = JSON.parse(savedTrack);
        console.log("🎵 Новый трек:", track.title);
        setCurrentTrack(track);

        // Автоматически начинаем воспроизведение
        if (audioRef.current && track.track_url) {
          audioRef.current.src = track.track_url;
          audioRef.current.play()
            .then(() => {
              setIsPlaying(true);
              console.log("▶️ Воспроизведение начато");
            })
            .catch(err => {
              console.error("Ошибка воспроизведения:", err);
              setIsPlaying(false);
            });
        } else if (!track.track_url) {
          console.warn("⚠️ У трека нет track_url");
        }
      }
    };

    const handlePlaylistChange = () => {
      console.log("📋 Событие playlistChanged получено");
      const savedPlaylist = localStorage.getItem("playlist");
      if (savedPlaylist) {
        setPlaylist(JSON.parse(savedPlaylist));
      }
    };

    // Подписываемся на события
    window.addEventListener("trackChanged", handleTrackChange);
    window.addEventListener("playlistChanged", handlePlaylistChange);

    // Проверяем, есть ли уже трек
    handleTrackChange();

    return () => {
      window.removeEventListener("trackChanged", handleTrackChange);
      window.removeEventListener("playlistChanged", handlePlaylistChange);
    };
  }, []);

  // ========== Сохранение состояния при изменении ==========

  useEffect(() => {
    if (currentTrack) {
      localStorage.setItem("currentTrack", JSON.stringify(currentTrack));
    }
    if (playlist.length > 0) {
      localStorage.setItem("playlist", JSON.stringify(playlist));
    }
    localStorage.setItem("currentIndex", String(currentIndex));
  }, [currentTrack, playlist, currentIndex]);

  // ========== Управление воспроизведением ==========

  const playTrack = (track, index = 0, tracks = []) => {
    if (!track?.track_url) {
      console.error("❌ Нет URL для воспроизведения");
      return;
    }

    console.log("🎵 playTrack вызван:", track.title);
    setCurrentTrack(track);
    setCurrentIndex(index);
    if (tracks.length > 0) setPlaylist(tracks);

    if (audioRef.current) {
      audioRef.current.src = track.track_url;
      audioRef.current.play()
        .then(() => {
          setIsPlaying(true);
          console.log("▶️ Воспроизведение начато");
          sendListening(track.track_id);
        })
        .catch(err => {
          console.error("❌ Ошибка воспроизведения:", err);
          setIsPlaying(false);
        });
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
        .catch(err => console.error("Ошибка воспроизведения:", err));
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current && !isDragging) {
      const current = audioRef.current.currentTime;
      const total = audioRef.current.duration || 0;
      setProgress(total > 0 ? (current / total) * 100 : 0);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
      console.log("📊 Длительность загружена:", audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    if (!hasTrack || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const seekTime = x * duration;
    if (audioRef.current) {
      audioRef.current.currentTime = seekTime;
      setProgress(x * 100);
    }
  };

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const playNext = () => {
    if (playlist.length === 0 || !hasTrack) return;
    let nextIndex = currentIndex + 1;
    if (nextIndex >= playlist.length) {
      if (isRepeated) nextIndex = 0;
      else return;
    }
    const nextTrack = playlist[nextIndex];
    if (nextTrack) {
      console.log("⏭ Следующий трек:", nextTrack.title);
      playTrack(nextTrack, nextIndex, playlist);
    }
  };

  const playPrevious = () => {
    if (playlist.length === 0 || !hasTrack) return;
    let prevIndex = currentIndex - 1;
    if (prevIndex < 0) prevIndex = playlist.length - 1;
    const prevTrack = playlist[prevIndex];
    if (prevTrack) {
      console.log("⏮ Предыдущий трек:", prevTrack.title);
      playTrack(prevTrack, prevIndex, playlist);
    }
  };

  const handleEnded = () => {
    console.log("⏹ Трек закончился");
    if (isRepeated && hasTrack && audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play();
    } else {
      playNext();
    }
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // ========== Рендер ==========

  return (
    <div className="bottom-player">

      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        onPlay={() => {
          setIsPlaying(true);
          console.log("▶️ onPlay");
        }}
        onPause={() => {
          setIsPlaying(false);
          console.log("⏸ onPause");
        }}
      />

      <div className="player-container">

        {/* ===== ЛЕВАЯ ЧАСТЬ ===== */}
        <div className="player-track-info">
          {hasTrack ? (
            <>
              <img
                src={currentTrack.cover_url || "https://picsum.photos/56"}
                alt={currentTrack.title || "Без названия"}
                className="player-cover"
                onClick={() => navigate(`/track/${currentTrack.track_id}`)}
              />
              <div className="player-track-meta">
                <span
                  className="player-track-title"
                  onClick={() => navigate(`/track/${currentTrack.track_id}`)}
                >
                  {currentTrack.title || "Без названия"}
                </span>
                <span
                  className="player-track-artist"
                  onClick={() => navigate(`/profile/${currentTrack.author_id}`)}
                >
                  {currentTrack.author_name || currentTrack.author_nickname || "Автор"}
                </span>
              </div>
              <div className="player-actions">
                <button
                  className={`like-btn ${isLiked ? "active" : ""}`}
                  onClick={() => setIsLiked(!isLiked)}
                >
                  {isLiked ? "❤️" : "🤍"}
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="player-cover placeholder" />
              <div className="player-track-meta">
                <span className="player-track-title placeholder-text">Ничего не играет</span>
                <span className="player-track-artist placeholder-text">Выберите трек</span>
              </div>
            </>
          )}
        </div>

        {/* ===== ЦЕНТРАЛЬНАЯ ЧАСТЬ ===== */}
        <div className="player-controls">

          <div className="player-controls-buttons">
            <button
              className={`control-btn ${isShuffled ? "active" : ""}`}
              onClick={() => setIsShuffled(!isShuffled)}
              disabled={!hasTrack}
            >
              🔀
            </button>
            <button
              className="control-btn"
              onClick={playPrevious}
              disabled={!hasTrack}
            >
              ⏮
            </button>
            <button
              className={`control-btn play-btn ${!hasTrack ? "disabled" : ""}`}
              onClick={togglePlay}
              disabled={!hasTrack}
            >
              {isPlaying ? "⏸" : "▶"}
            </button>
            <button
              className="control-btn"
              onClick={playNext}
              disabled={!hasTrack}
            >
              ⏭
            </button>
            <button
              className={`control-btn ${isRepeated ? "active" : ""}`}
              onClick={() => setIsRepeated(!isRepeated)}
              disabled={!hasTrack}
            >
              🔁
            </button>
          </div>

          <div className="player-progress">
            <span className="player-time">
              {hasTrack ? formatTime(audioRef.current?.currentTime || 0) : "0:00"}
            </span>
            <div
              className={`progress-bar ${!hasTrack ? "disabled" : ""}`}
              onClick={handleSeek}
              onMouseDown={handleMouseDown}
              onMouseUp={handleMouseUp}
            >
              <div
                className="progress-fill"
                style={{ width: `${hasTrack ? progress : 0}%` }}
              />
            </div>
            <span className="player-time">
              {hasTrack ? formatTime(duration) : "0:00"}
            </span>
          </div>

        </div>

        {/* ===== ПРАВАЯ ЧАСТЬ ===== */}
        <div className="player-volume">
          <span className="volume-icon">🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
            disabled={!hasTrack}
          />
        </div>

      </div>
    </div>
  );
}

export default BottomPlayer;