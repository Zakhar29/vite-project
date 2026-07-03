import { useMemo } from "react";
import { useParams } from "react-router-dom";
import CollectionHeader from "../components/CollectionHeader";
import CollectionTrackTable from "../components/CollectionTrackTable";
import {
  estimateTrackDuration,
  formatTotalDurationLabel,
} from "../utils/formatDuration";
import "../styles/collection.css";

const PLAYLISTS = {
  "user-tracks": {
    title: "Треки пользователя",
    subtitle: "Плейлист пользователя",
    description:
      "Все опубликованные треки автора в одном плейлисте. Удобно слушать подряд или перемешать для разнообразия.",
    coverUrl: "https://picsum.photos/seed/user-tracks/500/500",
    tracks: [
      { id: "pt-1", title: "Midnight Drive", artist_name: "Luna Waves", album_title: "Night Sessions", duration_seconds: 255, explicit: true },
      { id: "pt-2", title: "Soft Echo", artist_name: "Luna Waves", album_title: "Night Sessions", duration_seconds: 198 },
      { id: "pt-3", title: "City Lights", artist_name: "Luna Waves", album_title: "Urban Dreams", duration_seconds: 221, explicit: true },
      { id: "pt-4", title: "Afterglow", artist_name: "Luna Waves", album_title: "Urban Dreams", duration_seconds: 184 },
      { id: "pt-5", title: "Neon River", artist_name: "Luna Waves", album_title: "Singles", duration_seconds: 203 },
    ],
  },
  liked: {
    title: "Понравившееся",
    subtitle: "Плейлист пользователя",
    description:
      "Треки, которые вам понравились. Собраны в одном месте, чтобы быстро вернуться к любимому звучанию.",
    coverUrl: "https://picsum.photos/seed/liked/500/500",
    tracks: [
      { id: "lk-1", title: "Morning Coffee Jams", artist_name: "Various Artists", album_title: "Morning Coffee Jams", duration_seconds: 255 },
      { id: "lk-2", title: "Golden Hour", artist_name: "Sunset Crew", album_title: "Warm Days", duration_seconds: 212 },
      { id: "lk-3", title: "Low Tide", artist_name: "Ocean Room", album_title: "Coastal", duration_seconds: 241, explicit: true },
      { id: "lk-4", title: "Paper Planes", artist_name: "Indie Lab", album_title: "Sketches", duration_seconds: 196 },
      { id: "lk-5", title: "Velvet Sky", artist_name: "Night Forms", album_title: "After Dark", duration_seconds: 228 },
      { id: "lk-6", title: "Quiet Storm", artist_name: "Rain City", album_title: "Weather", duration_seconds: 205 },
      { id: "lk-7", title: "Last Train", artist_name: "Metro Soul", album_title: "Transit", duration_seconds: 267, explicit: true },
    ],
  },
  recent: {
    title: "Недавние",
    subtitle: "Плейлист пользователя",
    description:
      "Недавно прослушанные треки. Продолжайте с того места, где остановились, или откройте что-то новое из последних сессий.",
    coverUrl: "https://picsum.photos/seed/recent/500/500",
    tracks: [
      { id: "rc-1", title: "Evening Lights", artist_name: "Night Vibes", album_title: "City Dreams", duration_seconds: 235 },
      { id: "rc-2", title: "Ocean Breath", artist_name: "Calm Waves", album_title: "Sea Mood", duration_seconds: 261 },
      { id: "rc-3", title: "Soft Clouds", artist_name: "Dream Flow", album_title: "Sky Journey", duration_seconds: 302, explicit: true },
      { id: "rc-4", title: "Late Walk", artist_name: "Urban Steps", album_title: "Streets", duration_seconds: 189 },
    ],
  },
  default: {
    title: "Chill Evening",
    subtitle: "Плейлист пользователя",
    description:
      "Подборка спокойных треков для вечернего отдыха, расслабления и работы. Мягкие биты и тёплое настроение.",
    coverUrl: "https://picsum.photos/seed/chill-evening/500/500",
    tracks: [
      { id: "df-1", title: "Evening Lights", artist_name: "Night Vibes", album_title: "City Dreams", duration_seconds: 235 },
      { id: "df-2", title: "Ocean Breath", artist_name: "Calm Waves", album_title: "Sea Mood", duration_seconds: 261 },
      { id: "df-3", title: "Soft Clouds", artist_name: "Dream Flow", album_title: "Sky Journey", duration_seconds: 302, explicit: true },
      { id: "df-4", title: "Moonlit Room", artist_name: "Haze Unit", album_title: "Rooms", duration_seconds: 214 },
      { id: "df-5", title: "Slow Rivers", artist_name: "Field Notes", album_title: "Nature", duration_seconds: 248 },
    ],
  },
};

function Playlist() {
  const { id } = useParams();

  const playlist = PLAYLISTS[id] || PLAYLISTS.default;

  const tracks = useMemo(
    () =>
      playlist.tracks.map((track) => ({
        ...track,
        track_id: track.id,
        duration_seconds: track.duration_seconds || estimateTrackDuration(track),
        track_url: track.track_url || null,
      })),
    [playlist]
  );

  const metaLabel = useMemo(() => {
    const totalSeconds = tracks.reduce(
      (sum, track) => sum + (track.duration_seconds || 0),
      0
    );
    return formatTotalDurationLabel(tracks.length, totalSeconds);
  }, [tracks]);

  const startPlayback = (tracksList, startIndex = 0) => {
    const playable = tracksList.filter((t) => t.track_url);
    if (!playable.length) return;

    const track = playable[startIndex] || playable[0];
    localStorage.setItem("currentTrack", JSON.stringify(track));
    localStorage.setItem("playlist", JSON.stringify(playable));
    localStorage.setItem("currentIndex", String(startIndex));
    window.dispatchEvent(new Event("trackChanged"));
    window.dispatchEvent(new Event("playlistChanged"));
  };

  const playPlaylist = () => startPlayback(tracks, 0);

  const shufflePlaylist = () => {
    const shuffled = [...tracks].sort(() => Math.random() - 0.5);
    startPlayback(shuffled, 0);
  };

  const playTrack = (_track, index) => startPlayback(tracks, index);

  return (
    <div className="collection-page">
      <div className="collection-page__inner">
        <CollectionHeader
          coverUrl={playlist.coverUrl}
          title={playlist.title}
          subtitle={playlist.subtitle}
          description={playlist.description}
          metaLabel={metaLabel}
          onPlay={playPlaylist}
          onShuffle={shufflePlaylist}
          canPlay={tracks.some((t) => t.track_url)}
        />

        <CollectionTrackTable
          tracks={tracks}
          onPlayTrack={playTrack}
        />
      </div>

      <footer className="collection-page__footer">
        © 2025 Музыкальный сайт. Все права защищены.
      </footer>
    </div>
  );
}

export default Playlist;
