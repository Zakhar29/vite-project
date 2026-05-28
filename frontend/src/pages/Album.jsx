import { useParams } from "react-router-dom";
import "../styles/album.css";
import Navbar from "../components/Navbar";
import "../styles/track.css";

function Album() {
  return (
    
    
    <div className="album-page">

      <div className="album-header">

        <img
          src="https://picsum.photos/300"
          className="album-cover"
        />

        <div className="album-info">
          <h1>Morning Coffee Jams</h1>
          <p className="album-artist">Various Artists</p>

          <p className="album-desc">
            Идеальный альбом для расслабляющего вечера.
            Смесь спокойных мелодий и глубоких ритмов,
            которые помогут вам расслабиться.
          </p>

          <p className="album-meta">
            7 треков • 34 мин
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
              <td>Закат над городом</td>
              <td>Silent Waves</td>
              <td>Городские мечты</td>
              <td>4:15</td>
            </tr>

            <tr>
              <td>2</td>
              <td>Утренняя роса</td>
              <td>Ambient Journey</td>
              <td>Природа звука</td>
              <td>5:02</td>
            </tr>

            <tr>
              <td>3</td>
              <td>Потерянные мысли</td>
              <td>Echoes of Soul</td>
              <td>Глубокие эмоции</td>
              <td>3:48</td>
            </tr>

          </tbody>

        </table>

      </div>

    </div>
    
  );
}

export default Album;