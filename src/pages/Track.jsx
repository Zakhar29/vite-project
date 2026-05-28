import Navbar from "../components/Navbar";
import "../styles/track.css";

function Track() {
  return (
    <>
      <Navbar />

      <div className="track-page">
        <div className="track-content">

          {/* LEFT COLUMN */}
          <div className="left-column">

            <div className="track-main-card">
              <div className="track-text">
                <h1>Neon Dreamscape Anthem (Remix)</h1>
                <p className="artist-name">Savage Ginny</p>

                <div className="controls">
                  <button>▶</button>
                  <button>♡</button>
                  <button>↗</button>
                  <button>⋯</button>
                </div>

                <div className="progress-bar">
                  <span>0:34</span>
                  <input type="range" />
                  <span>3:04</span>
                </div>
                
              </div>

              <img
                src="https://picsum.photos/500/500?music"
                alt="cover"
                className="cover"
              />
            </div>

            {/* COMMENT INPUT */}
            <div className="comment-input">
              <textarea name="kik" id="kik" placeholder="Написать комментарий..."></textarea>
              <div className="comment-actions">
                <button className="cancel">Отмена</button>
                <button className="send">Отправить</button>
              </div>
            </div>

            {/* COMMENTS LIST */}
            <div className="comments">
              {[1, 2, 3, 4].map((item) => (
                <div key={item} className="comment">
                  <img src="https://picsum.photos/50" />
                  <div>
                    <div className="comment-header">
                      <strong>CodeWave_99</strong>
                      <span>2 часа назад</span>
                    </div>
                    <p>
                      В этом ремиксе все по-другому! Синтезаторы просто безумны.
                      Мне нравится их энергетика!
                    </p>
                    <div className="comment-footer">
                      <span>Ответить</span>
                      <span>❤ 12</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

          </div>

          {/* RIGHT COLUMN */}
          <div className="right-column">

            <div className="side-block">
              <h3>Артист</h3>
              <div className="artist-card">
                <img src="https://picsum.photos/80" />
                <div>
                  <p>Savage Ginny</p>
                  <button>Подписаться</button>
                </div>
              </div>
            </div>

            <div className="side-block">
              <h3>Теги</h3>
              <div className="tags">
                <span>#Electronic</span>
                <span>#FutureBass</span>
                <span>#Remix</span>
              </div>
            </div>

            <div className="side-block">
              <h3>Похожие треки</h3>
              {[1, 2, 3].map((item) => (
                <div key={item} className="mini-track">
                  <img src="https://picsum.photos/70" />
                  <div>
                    <p>Digital Echoes (Club Mix)</p>
                    <span>Future Groove</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="side-block">
              <h3>В плейлистах</h3>
              {[1, 2].map((item) => (
                <div key={item} className="mini-track">
                  <img src="https://picsum.photos/70?playlist" />
                  <div>
                    <p>Cyberpunk Essentials</p>
                    <span>18 треков</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="side-block">
              <h3>LIKED BY</h3>
              <div className="liked-users">
                <img src="https://picsum.photos/40?1" />
                <img src="https://picsum.photos/40?2" />
                <img src="https://picsum.photos/40?3" />
              </div>
            </div>

          </div>

        </div>
      </div>

      {/* STICKY PLAYER */}
      <div className="bottom-player">
        <div className="player-left">
          <button>▶</button>
          <span>0:34</span>
          <input type="range" />
          <span>3:04</span>
        </div>

        <div className="player-track-info">
          <img src="https://picsum.photos/50" />
          <div>
            <p>Neon Dreamscape Anthem (Remix)</p>
            <span>Savage Ginny</span>
          </div>
        </div>
      </div>
    </>
  );
}

export default Track;