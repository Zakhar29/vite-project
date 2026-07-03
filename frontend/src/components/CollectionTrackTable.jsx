import { useNavigate } from "react-router-dom";
import { formatTrackDuration } from "../utils/formatDuration";

function PlayRowIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
      <path fill="currentColor" d="M8 5v14l11-7z" />
    </svg>
  );
}

function CollectionTrackTable({ tracks = [], albumTitle = "", onPlayTrack }) {  const navigate = useNavigate();

  if (!tracks.length) {
    return (
      <section className="collection-tracks">
        <h2 className="collection-tracks__title">Треки</h2>
        <p className="collection-tracks__empty">Пока нет треков</p>
      </section>
    );
  }

  return (
    <section className="collection-tracks">
      <h2 className="collection-tracks__title">Треки</h2>

      <div className="collection-tracks__table-wrap">
        <table className="collection-tracks__table">
          <thead>
            <tr>
              <th className="col-num">#</th>
              <th className="col-title">Название</th>
              <th className="col-artist">Исполнитель</th>
              <th className="col-album">Альбом</th>
              <th className="col-duration">Продолжительность</th>
              <th className="col-options">Опции</th>
            </tr>
          </thead>
          <tbody>
            {tracks.map((track, index) => {
              const trackId = track.track_id || track.id;
              const artistName =
                track.artist_name ||
                track.author_name ||
                track.artist ||
                "Неизвестен";
              const albumName = track.album_title || albumTitle || "—";
              const duration = formatTrackDuration(
                track.duration_seconds ?? track.duration
              );
              const canPlay = Boolean(track.track_url);

              return (
                <tr
                  key={trackId || index}
                  className="collection-tracks__row"
                  onDoubleClick={() => canPlay && onPlayTrack?.(track, index)}
                >
                  <td className="col-num">
                    <span className="collection-tracks__index">{index + 1}</span>
                    <button
                      type="button"
                      className="collection-tracks__play"
                      aria-label={`Воспроизвести ${track.title}`}
                      disabled={!canPlay}
                      onClick={(e) => {
                        e.stopPropagation();
                        onPlayTrack?.(track, index);
                      }}
                    >
                      <PlayRowIcon />
                    </button>
                  </td>
                  <td className="col-title">
                    <button
                      type="button"
                      className="collection-tracks__title-btn"
                      onClick={() => trackId && navigate(`/track/${trackId}`)}
                    >
                      {track.title}
                    </button>
                    {track.explicit && (
                      <span className="collection-tracks__explicit">EXPLICIT</span>
                    )}
                  </td>
                  <td className="col-artist">{artistName}</td>
                  <td className="col-album">{albumName}</td>
                  <td className="col-duration">{duration}</td>
                  <td className="col-options">
                    <button
                      type="button"
                      className="collection-tracks__options"
                      aria-label="Опции"
                    >
                      ⋯
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default CollectionTrackTable;
