import { useState, useEffect, useMemo } from "react";
import { useParams } from "react-router-dom";
import CollectionHeader from "../components/CollectionHeader";
import CollectionTrackTable from "../components/CollectionTrackTable";
import {
  estimateTrackDuration,
  formatTotalDurationLabel,
} from "../utils/formatDuration";
import "../styles/collection.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Album() {
  const { id } = useParams();
  const token = localStorage.getItem("access_token");

  const [album, setAlbum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLiked, setIsLiked] = useState(false);

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
        if (response.status === 404) throw new Error("Альбом не найден");
        throw new Error("Ошибка загрузки альбома");
      }

      const data = await response.json();
      setAlbum(data.album);
      setIsLiked(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const enrichedTracks = useMemo(() => {
    if (!album?.tracks) return [];
    return album.tracks.map((track) => ({
      ...track,
      artist_name: album.author?.nickname || "Неизвестный автор",
      album_title: album.title,
      duration_seconds: estimateTrackDuration(track),
    }));
  }, [album]);

  const metaLabel = useMemo(() => {
    const totalSeconds = enrichedTracks.reduce(
      (sum, track) => sum + (track.duration_seconds || 0),
      0
    );
    return formatTotalDurationLabel(enrichedTracks.length, totalSeconds);
  }, [enrichedTracks]);

  const description = useMemo(() => {
    if (album?.description) return album.description;
    const author = album?.author?.nickname || "артиста";
    const typeLabel = album?.type?.toLowerCase?.() || "альбом";
    return `Подборка треков в формате ${typeLabel} от ${author}. Идеально для полного погружения в звучание и настроение релиза.`;
  }, [album]);

  const buildPlayerTracks = (tracksList) =>
    tracksList.map((track) => ({
      ...track,
      id: track.track_id,
      author_name: album.author?.nickname || "Неизвестный автор",
      author_id: album.author?.id,
      cover_url: album.cover_url,
    }));

  const startPlayback = (tracksList, startIndex = 0) => {
    if (!tracksList.length) return;

    const playlist = buildPlayerTracks(tracksList);
    const track = playlist[startIndex];

    if (!track?.track_url) {
      return;
    }

    localStorage.setItem("currentTrack", JSON.stringify(track));
    localStorage.setItem("playlist", JSON.stringify(playlist));
    localStorage.setItem("currentIndex", String(startIndex));
    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  const playAlbum = () => startPlayback(enrichedTracks, 0);

  const shuffleAlbum = () => {
    const shuffled = [...enrichedTracks].sort(() => Math.random() - 0.5);
    startPlayback(shuffled, 0);
  };

  const playTrack = (track, index) => {
    startPlayback(enrichedTracks, index);
  };

  const handleLike = async () => {
    if (!token) return;

    const url = `${API_URL}/api/v1/social/album/${id}/${isLiked ? "unlike" : "like"}`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        setIsLiked(!isLiked);
        setAlbum((prev) => ({
          ...prev,
          liked_quantity: (prev.liked_quantity || 0) + (isLiked ? -1 : 1),
        }));
      }
    } catch (err) {
      console.error("Ошибка лайка:", err);
    }
  };

  if (loading) {
    return (
      <div className="collection-page">
        <div className="collection-page__state">
          <div className="loading-spinner" />
          <p>Загрузка альбома...</p>
        </div>
      </div>
    );
  }

  if (error || !album) {
    return (
      <div className="collection-page">
        <div className="collection-page__state">
          <h2>{error || "Альбом не найден"}</h2>
          <button type="button" onClick={loadAlbumData}>
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="collection-page">
      <div className="collection-page__inner">
        <CollectionHeader
          coverUrl={album.cover_url}
          title={album.title}
          subtitle={album.author?.nickname || "Неизвестный автор"}
          subtitleTo={album.author?.id ? `/profile/${album.author.id}` : undefined}
          description={description}
          metaLabel={metaLabel}
          onPlay={playAlbum}
          onShuffle={shuffleAlbum}
          onLike={handleLike}
          isLiked={isLiked}
          canPlay={enrichedTracks.some((t) => t.track_url)}
        />

        <CollectionTrackTable
          tracks={enrichedTracks}
          albumTitle={album.title}
          onPlayTrack={playTrack}
        />
      </div>

      <footer className="collection-page__footer">
        © 2025 Музыкальный сайт. Все права защищены.
      </footer>
    </div>
  );
}

export default Album;
