function PackHeader() {
  return (
    <div className="pack-header">

      <img
        src="https://picsum.photos/400"
        className="pack-cover"
      />

      <div className="pack-info">

        <h1>Глубокие басовые в стиле Хаус</h1>

        <span className="author">CyberSynth Audio</span>

        <p>
          Окунитесь в атмосферу будущего с этим
          эксклюзивным пакетом звуков.
        </p>

        <div className="pack-tags">
          <span>Киберпанк</span>
          <span>Электроника</span>
          <span>Синтезаторы</span>
          <span>Эмбиент</span>
        </div>

        <div className="pack-stats">
          <span>⬇ 12,589 загрузок</span>
          <span>💾 750 MB</span>
        </div>

        <button className="download-btn">
          Скачать пакет
        </button>

      </div>

    </div>
  );
}

export default PackHeader;