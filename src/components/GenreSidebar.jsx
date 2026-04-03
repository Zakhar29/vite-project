function GenreSidebar() {
  return (
    <div className="genre-sidebar">

      <h3>ЖАНРЫ</h3>

      <ul>
        <li>⚡ Электронная</li>
        <li>🎸 Рок</li>
        <li>🎧 Хип-хоп</li>
        <li>❤️ Поп</li>
        <li>🎻 Классическая</li>
      </ul>

      <div className="genre-extra">
        <p>В тренде</p>
        <p>Новое</p>
        <p>Моё</p>
      </div>

    </div>
  );
}

export default GenreSidebar;