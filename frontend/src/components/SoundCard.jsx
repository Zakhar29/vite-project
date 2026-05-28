function SoundCard() {
  return (
    <div className="sound-card">

      <div className="sound-image">

        <img
          src="https://picsum.photos/300/200"
          alt=""
        />

        <button className="play">▶</button>

      </div>

      <div className="sound-info">

        <span className="tag">Samples</span>

        <h3>Глубокие басовые петли в стиле Хаус</h3>

        <p className="author">by Groove Labs</p>

        <div className="genres">
          <span>Deep House</span>
          <span>Bass</span>
          <span>Loops</span>
          <span>Electronic</span>
        </div>

        <div className="card-actions">
          <button className="download">Скачать</button>
          <button className="add">Добавить</button>
        </div>

      </div>

    </div>
  );
}

export default SoundCard;