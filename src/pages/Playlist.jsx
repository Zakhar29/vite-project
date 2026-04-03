import "../styles/album.css";

function Playlist() {
  return (
    <div className="album-page">

      <div className="album-header">

        <img
          src="https://picsum.photos/300?playlist"
          className="album-cover"
        />

        <div className="album-info">
          <h1>Chill Evening</h1>

          <p className="album-artist">
            Плейлист пользователя
          </p>

          <p className="album-desc">
            Подборка спокойных треков для вечернего отдыха,
            расслабления и работы.
          </p>

          <p className="album-meta">
            12 треков • 48 мин
          </p>

          <div className="album-buttons">
            <button className="play-btn">▶ Воспроизвести</button>
            <button className="shuffle-btn">🔀 Перемешать</button>
          </div>
        </div>

      </div>


      <div className="tracks">

        <h2>Треки</h2>

        <table className="tracks-table">

          <thead>
            <tr>
              <th>#</th>
              <th>Название</th>
              <th>Исполнитель</th>
              <th>Альбом</th>
              <th>Длительность</th>
            </tr>
          </thead>

          <tbody>

            <tr>
              <td>1</td>
              <td>Evening Lights</td>
              <td>Night Vibes</td>
              <td>City Dreams</td>
              <td>3:55</td>
            </tr>

            <tr>
              <td>2</td>
              <td>Ocean Breath</td>
              <td>Calm Waves</td>
              <td>Sea Mood</td>
              <td>4:21</td>
            </tr>

            <tr>
              <td>3</td>
              <td>Soft Clouds</td>
              <td>Dream Flow</td>
              <td>Sky Journey</td>
              <td>5:02</td>
            </tr>

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default Playlist;