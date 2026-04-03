function PackSidebar() {
  return (
    <div className="sidebar-recommend">

      <h3>Вам также может понравиться</h3>

      <div className="recommend-card">
        <img src="https://picsum.photos/80" />
        <div>
          <p>Космическая Одиссея</p>
          <span>StarDust Beats</span>
        </div>
      </div>

      <div className="recommend-card">
        <img src="https://picsum.photos/81" />
        <div>
          <p>Ретро Вейв Сборник</p>
          <span>80s Rewind</span>
        </div>
      </div>

      <div className="recommend-card">
        <img src="https://picsum.photos/82" />
        <div>
          <p>Лоу-фай Хип-Хоп Биты</p>
          <span>ChillGrooves</span>
        </div>
      </div>

    </div>
  );
}

export default PackSidebar;